# src/simulacrum/digital_twin/twin.py
"""
Digital Twin core implementation.

A digital twin is a personalized AI replica of a specific individual,
capturing their personality, behavior patterns, and decision-making style.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

from ..agents.persona import PsychologicalProfile, Citizen
from ..core.memory import Memory
from ..utils.exceptions import CalibrationError, InsufficientDataError


def _estimate_traits_from_partial(responses: Dict[str, Any]) -> "PsychologicalProfile":
    """
    Estimate Big Five traits from partial/informal survey responses.

    Looks for keys containing trait names (openness_*, conscientiousness_*, etc.)
    and averages the provided scores (assumed 1-5 scale → 0.0-1.0).
    Missing traits default to 0.5.
    """
    trait_names = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]
    scores: Dict[str, list] = {t: [] for t in trait_names}

    for key, value in responses.items():
        key_lower = key.lower()
        for trait in trait_names:
            if trait in key_lower or trait[:4] in key_lower:
                try:
                    numeric = float(value)
                    # Normalise from 1-5 to 0.0-1.0
                    scores[trait].append((numeric - 1) / 4)
                except (TypeError, ValueError):
                    pass

    trait_values = {
        t: (sum(v) / len(v) if v else 0.5) for t, v in scores.items()
    }
    return PsychologicalProfile(**trait_values)


@dataclass
class Decision:
    """
    A simulated decision made by a digital twin.
    
    Attributes:
        recommendation: The recommended choice ("Accept", "Decline", etc.)
        reasoning: Natural language explanation
        confidence: Confidence score (0.0-1.0)
        alternatives_considered: Other options evaluated
        personality_factors: Which traits influenced the decision
        timestamp: When decision was made
        context: Original decision context
    """
    recommendation: str
    reasoning: str
    confidence: float
    alternatives_considered: List[str] = field(default_factory=list)
    personality_factors: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "recommendation": self.recommendation,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "alternatives_considered": self.alternatives_considered,
            "personality_factors": self.personality_factors,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Decision":
        """Deserialize from dictionary."""
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


class DigitalTwin:
    """
    A personalized AI replica of a specific individual.
    
    Digital twins capture personality, behavior patterns, and decision-making
    style to simulate how a specific person would act in various scenarios.
    
    Examples:
        >>> # Create from survey
        >>> twin = DigitalTwin.from_survey(survey_responses, name="Alice")
        >>> 
        >>> # Simulate decision
        >>> decision = twin.simulate_decision(
        ...     question="Should I accept this job offer?",
        ...     context={"salary": 120000, "role": "Senior Engineer"}
        ... )
        >>> print(decision.recommendation)  # "Accept" or "Decline"
        >>> print(decision.reasoning)       # Why
        >>> print(decision.confidence)      # 0.85
        
    Attributes:
        name (str): Person's name
        traits (PsychologicalProfile): Big Five personality traits
        memory (Memory): Personal history and experiences
        calibration_score (float): Accuracy of calibration (0.0-1.0)
    """
    
    def __init__(
        self,
        name: str,
        traits: PsychologicalProfile,
        memory: Optional[Memory] = None,
        calibration_data: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Initialize digital twin.
        
        Args:
            name: Person's name
            traits: Personality traits (Big Five)
            memory: Optional memory system
            calibration_data: Optional calibration information
            metadata: Optional additional metadata
        """
        self.name = name
        self.traits = traits
        self.memory = memory or Memory()
        self.calibration_data = calibration_data or {}
        self.metadata = metadata or {}
        
        # Internal state
        self._calibration_score = 0.0
        self._decision_history: List[Decision] = []
        self._created_at = datetime.now()
        
    @classmethod
    def from_survey(
        cls,
        survey_responses: Dict[str, Any],
        name: Optional[str] = None,
        **kwargs
    ) -> "DigitalTwin":
        """
        Create digital twin from personality survey.
        
        Args:
            survey_responses: Responses to personality assessment
            name: Optional name for the twin
            **kwargs: Additional configuration
            
        Returns:
            Calibrated DigitalTwin instance
            
        Raises:
            InsufficientDataError: If responses are incomplete
            
        Examples:
            >>> responses = {
            ...     "openness_1": 5,
            ...     "openness_2": 4,
            ...     # ... 50 questions total
            ... }
            >>> twin = DigitalTwin.from_survey(responses, name="Alice")
            >>> print(f"Calibration: {twin.get_calibration_score():.1%}")
        """
        from .calibration import PersonalityAssessment
        
        # Validate responses
        if not survey_responses:
            raise InsufficientDataError(
                "Survey responses cannot be empty",
                missing_fields=["survey_responses"]
            )
        
        # Calculate traits — fall back to simple estimation for partial responses
        assessment = PersonalityAssessment()
        try:
            traits = assessment.calculate_traits(survey_responses)
            confidence = assessment.get_confidence()
        except (ValueError, KeyError):
            traits = _estimate_traits_from_partial(survey_responses)
            n = len(survey_responses)
            confidence = min(0.3 + (n / 50) * 0.5, 0.8)
        
        # Create twin
        twin = cls(
            name=name or "User",
            traits=traits,
            calibration_data={
                "method": "survey",
                "assessment_confidence": confidence,
                "questions_answered": len(survey_responses)
            }
        )
        twin._calibration_score = confidence
        
        return twin
    
    @classmethod
    def from_behavioral_data(
        cls,
        behavioral_history: List[Dict],
        name: Optional[str] = None,
        **kwargs
    ) -> "DigitalTwin":
        """
        Create digital twin from observed behavior.
        
        Args:
            behavioral_history: Past decisions and outcomes
            name: Optional name
            **kwargs: Additional configuration
            
        Returns:
            Calibrated DigitalTwin
            
        Raises:
            InsufficientDataError: If history too short
            
        Examples:
            >>> history = [
            ...     {"decision": "Took risky project", "outcome": "success"},
            ...     {"decision": "Avoided conflict", "outcome": "neutral"},
            ...     # ... minimum 10 events
            ... ]
            >>> twin = DigitalTwin.from_behavioral_data(history, name="Bob")
        """
        from .calibration import BehavioralCalibrator
        
        # Validate history
        if len(behavioral_history) < 10:
            raise InsufficientDataError(
                "Need at least 10 behavioral events for calibration",
                missing_fields=["behavioral_history"],
                suggestions=["Provide more past decisions and outcomes"]
            )
        
        # Infer traits
        calibrator = BehavioralCalibrator()
        traits = calibrator.infer_traits(behavioral_history)
        confidence = calibrator.get_confidence()
        
        # Create twin
        twin = cls(
            name=name or "User",
            traits=traits,
            calibration_data={
                "method": "behavioral",
                "events_analyzed": len(behavioral_history),
                "inference_confidence": confidence
            }
        )
        twin._calibration_score = confidence
        
        # Add history to memory
        for event in behavioral_history:
            twin.memory.add(event)
        
        return twin
    
    def simulate_decision(
        self,
        question: str,
        context: Optional[Dict] = None,
        use_memory: bool = True,
        explain: bool = True
    ) -> Decision:
        """
        Simulate how this person would decide.
        
        Args:
            question: Decision to make
            context: Additional context
            use_memory: Whether to use past experiences
            explain: Whether to include detailed reasoning
            
        Returns:
            Decision with recommendation, reasoning, confidence
            
        Examples:
            >>> decision = twin.simulate_decision(
            ...     "Accept job offer at startup?",
            ...     context={"salary": 100000, "equity": "0.5%", "risk": "high"}
            ... )
            >>> print(f"{decision.recommendation}: {decision.reasoning}")
            >>> print(f"Confidence: {decision.confidence:.0%}")
        """
        # Construct decision context
        full_context = {
            "personality": self.traits.to_dict(),
            "question": question,
            "person_name": self.name,
            **(context or {})
        }
        
        # Add relevant memories if requested
        relevant_memories = []
        if use_memory and len(self.memory.events) > 0:
            relevant_memories = self._get_relevant_memories(question, limit=5)
            if relevant_memories:
                full_context["past_experiences"] = relevant_memories
        
        # Generate decision (using personality + context)
        decision = self._generate_decision(full_context, explain=explain)
        
        # Store decision in history
        self._decision_history.append(decision)
        
        # Log decision to memory
        self.memory.add({
            "type": "decision_simulation",
            "question": question,
            "recommendation": decision.recommendation,
            "confidence": decision.confidence,
            "context": context,
            "timestamp": decision.timestamp.isoformat()
        })
        
        return decision
    
    def calibrate(
        self,
        test_scenarios: List[Dict],
        actual_choices: List[str],
        update_score: bool = True
    ) -> float:
        """
        Calibrate twin accuracy using known decisions.
        
        Args:
            test_scenarios: Scenarios to test
            actual_choices: What person actually chose
            update_score: Whether to update calibration score
            
        Returns:
            Calibration accuracy (0.0-1.0)
            
        Raises:
            CalibrationError: If scenarios/choices length mismatch
            
        Examples:
            >>> scenarios = [
            ...     {"question": "Take risky investment?", "context": {...}},
            ...     {"question": "Confront colleague?", "context": {...}},
            ...     # ... 10-20 scenarios recommended
            ... ]
            >>> actual = ["Decline", "Accept", ...]
            >>> accuracy = twin.calibrate(scenarios, actual)
            >>> print(f"Twin accuracy: {accuracy:.1%}")
        """
        if len(test_scenarios) != len(actual_choices):
            raise CalibrationError(
                f"Scenarios ({len(test_scenarios)}) and choices ({len(actual_choices)}) "
                f"must have same length"
            )
        
        if len(test_scenarios) < 5:
            raise CalibrationError(
                "Need at least 5 test scenarios for meaningful calibration"
            )
        
        correct = 0
        results = []
        
        for scenario, actual in zip(test_scenarios, actual_choices):
            # Simulate decision
            predicted = self.simulate_decision(
                scenario["question"],
                scenario.get("context"),
                use_memory=False  # Don't use memory for calibration
            )
            
            # Check if correct
            is_correct = self._normalize_choice(predicted.recommendation) == \
                        self._normalize_choice(actual)
            
            if is_correct:
                correct += 1
            
            results.append({
                "scenario": scenario["question"],
                "predicted": predicted.recommendation,
                "actual": actual,
                "correct": is_correct,
                "confidence": predicted.confidence
            })
        
        # Calculate accuracy
        accuracy = correct / len(test_scenarios)
        
        # Update calibration data
        self.calibration_data["calibration_results"] = results
        self.calibration_data["calibration_accuracy"] = accuracy
        self.calibration_data["calibration_date"] = datetime.now().isoformat()
        
        if update_score:
            self._calibration_score = accuracy
        
        return accuracy
    
    def get_calibration_score(self) -> float:
        """
        Get current calibration accuracy.
        
        Returns:
            Calibration score (0.0-1.0)
        """
        return self._calibration_score
    
    def get_decision_history(self, limit: Optional[int] = None) -> List[Decision]:
        """
        Get history of simulated decisions.
        
        Args:
            limit: Optional max number of decisions to return
            
        Returns:
            List of Decision objects (most recent first)
        """
        history = sorted(
            self._decision_history,
            key=lambda d: d.timestamp,
            reverse=True
        )
        
        if limit:
            return history[:limit]
        return history
    
    def explain_decision(self, decision: Decision) -> str:
        """
        Explain why twin made this decision.
        
        Args:
            decision: Decision to explain
            
        Returns:
            Natural language explanation
            
        Examples:
            >>> decision = twin.simulate_decision("Launch risky feature?")
            >>> explanation = twin.explain_decision(decision)
            >>> print(explanation)
        """
        from ..governance.explainability import ExplainabilityEngine
        
        explainer = ExplainabilityEngine(self)
        return explainer.explain_decision(decision, self)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "name": self.name,
            "traits": self.traits.to_dict(),
            "calibration_score": self._calibration_score,
            "calibration_data": self.calibration_data,
            "memory": self.memory.to_dict() if hasattr(self.memory, 'to_dict') else {},
            "decision_count": len(self._decision_history),
            "created_at": self._created_at.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DigitalTwin":
        """
        Deserialize from dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            DigitalTwin instance
        """
        traits = PsychologicalProfile.from_dict(data["traits"])
        memory = Memory.from_dict(data.get("memory", {})) if "memory" in data else Memory()
        
        twin = cls(
            name=data["name"],
            traits=traits,
            memory=memory,
            calibration_data=data.get("calibration_data", {}),
            metadata=data.get("metadata", {})
        )
        twin._calibration_score = data.get("calibration_score", 0.0)
        
        if "created_at" in data:
            twin._created_at = datetime.fromisoformat(data["created_at"])
        
        return twin
    
    def save(self, filepath: str) -> None:
        """
        Save digital twin to file.
        
        Args:
            filepath: Path to save file (.json)
        """
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, filepath: str) -> "DigitalTwin":
        """
        Load digital twin from file.
        
        Args:
            filepath: Path to saved file (.json)
            
        Returns:
            DigitalTwin instance
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    # Private methods
    
    def _generate_decision(
        self,
        context: Dict[str, Any],
        explain: bool = True
    ) -> Decision:
        """
        Generate decision based on personality and context.
        
        This is a simplified implementation. In production, this would:
        1. Use LLM with personality prompt
        2. Consider past experiences
        3. Apply learned strategies
        4. Factor in current emotional state
        """
        # Extract question
        question = context.get("question", "")
        
        # Analyze personality influence
        personality_factors = self._analyze_personality_influence(context)
        
        # Simple decision logic (placeholder for LLM)
        # In production: Call LLM with personality-infused prompt
        recommendation = self._make_personality_based_choice(context, personality_factors)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            recommendation,
            personality_factors,
            context
        ) if explain else "Decision based on personality analysis"
        
        # Calculate confidence
        confidence = self._calculate_confidence(personality_factors)
        
        return Decision(
            recommendation=recommendation,
            reasoning=reasoning,
            confidence=confidence,
            personality_factors=personality_factors,
            context=context
        )
    
    def _analyze_personality_influence(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Analyze which personality traits influence this decision."""
        factors = {}
        
        # Check for risk-related context
        if any(keyword in str(context).lower() for keyword in ["risk", "uncertain", "new"]):
            factors["openness"] = self.traits.openness
            factors["neuroticism"] = self.traits.neuroticism
        
        # Check for social context
        if any(keyword in str(context).lower() for keyword in ["team", "people", "collaborate"]):
            factors["agreeableness"] = self.traits.agreeableness
            factors["extraversion"] = self.traits.extraversion
        
        # Check for planning context
        if any(keyword in str(context).lower() for keyword in ["plan", "organize", "detail"]):
            factors["conscientiousness"] = self.traits.conscientiousness
        
        return factors
    
    def _make_personality_based_choice(
        self,
        context: Dict[str, Any],
        factors: Dict[str, float]
    ) -> str:
        """Make choice based on personality (simplified logic)."""
        # Simple heuristic (in production: use LLM)
        risk_tolerance = self.traits.openness - self.traits.neuroticism
        
        if "risk" in str(context).lower():
            return "Accept" if risk_tolerance > 0.5 else "Decline"
        
        # Default: cautious accept
        return "Accept" if self.traits.conscientiousness > 0.6 else "Decline"
    
    def _generate_reasoning(
        self,
        recommendation: str,
        factors: Dict[str, float],
        context: Dict[str, Any]
    ) -> str:
        """Generate explanation for decision."""
        # Simplified reasoning (in production: use LLM)
        reasons = []
        
        if "openness" in factors:
            if factors["openness"] > 0.7:
                reasons.append("I'm naturally inclined toward new experiences")
            elif factors["openness"] < 0.4:
                reasons.append("I prefer proven approaches")
        
        if "neuroticism" in factors:
            if factors["neuroticism"] > 0.6:
                reasons.append("but I'm cautious about potential risks")
            elif factors["neuroticism"] < 0.4:
                reasons.append("and I'm comfortable with uncertainty")
        
        if not reasons:
            reasons.append(f"Based on careful consideration, I would {recommendation.lower()}")
        
        return ". ".join(reasons) + "."
    
    def _calculate_confidence(self, factors: Dict[str, float]) -> float:
        """Calculate confidence score."""
        if not factors:
            return 0.5  # Neutral confidence
        
        # Higher variance in personality = lower confidence
        variance = sum((v - 0.5) ** 2 for v in factors.values()) / len(factors)
        confidence = 0.6 + (variance * 0.4)  # Scale to 0.6-1.0
        
        return min(max(confidence, 0.0), 1.0)
    
    def _get_relevant_memories(self, query: str, limit: int = 5) -> List[Dict]:
        """Get memories relevant to query."""
        # Simplified memory search
        if not hasattr(self.memory, 'search'):
            return []
        
        return self.memory.search(query, limit=limit)
    
    def _normalize_choice(self, choice: str) -> str:
        """Normalize choice for comparison."""
        choice = choice.lower().strip()
        
        # Map common variations
        accept_variants = ["yes", "accept", "agree", "approve", "go ahead"]
        decline_variants = ["no", "decline", "reject", "refuse", "pass"]
        
        if any(v in choice for v in accept_variants):
            return "accept"
        elif any(v in choice for v in decline_variants):
            return "decline"
        
        return choice
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"DigitalTwin(name='{self.name}', "
            f"calibration={self._calibration_score:.2f}, "
            f"decisions={len(self._decision_history)})"
        )
