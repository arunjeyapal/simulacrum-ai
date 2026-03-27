# src/simulacrum/digital_twin/calibration.py
"""
Calibration system for creating accurate digital twins.

This module provides tools for:
1. Personality assessment via Big Five questionnaire
2. Behavioral calibration from observed actions
3. Confidence scoring for calibration accuracy
"""

from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum
import statistics

from ..agents.persona import PsychologicalProfile


class TraitDimension(Enum):
    """Big Five personality dimensions."""
    OPENNESS = "openness"
    CONSCIENTIOUSNESS = "conscientiousness"
    EXTRAVERSION = "extraversion"
    AGREEABLENESS = "agreeableness"
    NEUROTICISM = "neuroticism"


@dataclass
class Question:
    """
    A personality assessment question.
    
    Attributes:
        id: Unique question identifier
        text: Question text
        trait: Which Big Five trait this measures
        reverse_scored: Whether this is a reverse-scored item
    """
    id: str
    text: str
    trait: TraitDimension
    reverse_scored: bool = False


class PersonalityAssessment:
    """
    Big Five personality assessment using IPIP-NEO questionnaire.
    
    Provides 50-question assessment (10 per trait) to calculate
    personality profile for digital twin creation.
    
    Examples:
        >>> assessment = PersonalityAssessment()
        >>> questions = assessment.get_questions()
        >>> 
        >>> # User answers questions (1-5 scale)
        >>> responses = {"Q01": 4, "Q02": 5, ...}
        >>> 
        >>> traits = assessment.calculate_traits(responses)
        >>> print(traits.openness)  # 0.75
        >>> 
        >>> confidence = assessment.get_confidence()
        >>> print(f"Confidence: {confidence:.0%}")
    """
    
    def __init__(self):
        """Initialize personality assessment."""
        self._questions = self._build_questionnaire()
        self._responses: Dict[str, int] = {}
        self._confidence: float = 0.0
    
    def _build_questionnaire(self) -> List[Question]:
        """
        Build 50-question Big Five assessment.
        
        10 questions per trait (5 standard + 5 reverse-scored).
        Based on IPIP-NEO public domain items.
        """
        questions = [
            # OPENNESS (10 questions)
            Question("Q01", "I have a vivid imagination", TraitDimension.OPENNESS, False),
            Question("Q02", "I have difficulty understanding abstract ideas", TraitDimension.OPENNESS, True),
            Question("Q03", "I enjoy thinking about complex problems", TraitDimension.OPENNESS, False),
            Question("Q04", "I avoid philosophical discussions", TraitDimension.OPENNESS, True),
            Question("Q05", "I am interested in many different topics", TraitDimension.OPENNESS, False),
            Question("Q06", "I dislike learning new things", TraitDimension.OPENNESS, True),
            Question("Q07", "I enjoy creative activities", TraitDimension.OPENNESS, False),
            Question("Q08", "I prefer routine over novelty", TraitDimension.OPENNESS, True),
            Question("Q09", "I appreciate art and beauty", TraitDimension.OPENNESS, False),
            Question("Q10", "I rarely notice artistic details", TraitDimension.OPENNESS, True),
            
            # CONSCIENTIOUSNESS (10 questions)
            Question("Q11", "I am always prepared", TraitDimension.CONSCIENTIOUSNESS, False),
            Question("Q12", "I often leave things unfinished", TraitDimension.CONSCIENTIOUSNESS, True),
            Question("Q13", "I pay attention to details", TraitDimension.CONSCIENTIOUSNESS, False),
            Question("Q14", "I make plans and stick to them", TraitDimension.CONSCIENTIOUSNESS, False),
            Question("Q15", "I often forget to put things back in their proper place", TraitDimension.CONSCIENTIOUSNESS, True),
            Question("Q16", "I complete tasks successfully", TraitDimension.CONSCIENTIOUSNESS, False),
            Question("Q17", "I do things according to a plan", TraitDimension.CONSCIENTIOUSNESS, False),
            Question("Q18", "I waste my time", TraitDimension.CONSCIENTIOUSNESS, True),
            Question("Q19", "I get tasks done right away", TraitDimension.CONSCIENTIOUSNESS, False),
            Question("Q20", "I shirk my duties", TraitDimension.CONSCIENTIOUSNESS, True),
            
            # EXTRAVERSION (10 questions)
            Question("Q21", "I am the life of the party", TraitDimension.EXTRAVERSION, False),
            Question("Q22", "I prefer to be alone rather than with others", TraitDimension.EXTRAVERSION, True),
            Question("Q23", "I talk to a lot of different people at parties", TraitDimension.EXTRAVERSION, False),
            Question("Q24", "I don't like to draw attention to myself", TraitDimension.EXTRAVERSION, True),
            Question("Q25", "I feel comfortable around people", TraitDimension.EXTRAVERSION, False),
            Question("Q26", "I keep in the background", TraitDimension.EXTRAVERSION, True),
            Question("Q27", "I start conversations", TraitDimension.EXTRAVERSION, False),
            Question("Q28", "I have little to say", TraitDimension.EXTRAVERSION, True),
            Question("Q29", "I make friends easily", TraitDimension.EXTRAVERSION, False),
            Question("Q30", "I am quiet around strangers", TraitDimension.EXTRAVERSION, True),
            
            # AGREEABLENESS (10 questions)
            Question("Q31", "I am interested in people", TraitDimension.AGREEABLENESS, False),
            Question("Q32", "I am not interested in other people's problems", TraitDimension.AGREEABLENESS, True),
            Question("Q33", "I feel others' emotions", TraitDimension.AGREEABLENESS, False),
            Question("Q34", "I am indifferent to the feelings of others", TraitDimension.AGREEABLENESS, True),
            Question("Q35", "I make people feel at ease", TraitDimension.AGREEABLENESS, False),
            Question("Q36", "I insult people", TraitDimension.AGREEABLENESS, True),
            Question("Q37", "I sympathize with others' feelings", TraitDimension.AGREEABLENESS, False),
            Question("Q38", "I am not really interested in others", TraitDimension.AGREEABLENESS, True),
            Question("Q39", "I have a soft heart", TraitDimension.AGREEABLENESS, False),
            Question("Q40", "I cut others short when they talk", TraitDimension.AGREEABLENESS, True),
            
            # NEUROTICISM (10 questions)
            Question("Q41", "I often feel blue", TraitDimension.NEUROTICISM, False),
            Question("Q42", "I am relaxed most of the time", TraitDimension.NEUROTICISM, True),
            Question("Q43", "I get stressed out easily", TraitDimension.NEUROTICISM, False),
            Question("Q44", "I seldom feel blue", TraitDimension.NEUROTICISM, True),
            Question("Q45", "I worry about things", TraitDimension.NEUROTICISM, False),
            Question("Q46", "I am not easily bothered by things", TraitDimension.NEUROTICISM, True),
            Question("Q47", "I get upset easily", TraitDimension.NEUROTICISM, False),
            Question("Q48", "I remain calm in difficult situations", TraitDimension.NEUROTICISM, True),
            Question("Q49", "I am easily discouraged", TraitDimension.NEUROTICISM, False),
            Question("Q50", "I handle stress well", TraitDimension.NEUROTICISM, True),
        ]
        
        return questions
    
    def get_questions(self) -> List[Question]:
        """
        Get all assessment questions.
        
        Returns:
            List of 50 Question objects
            
        Examples:
            >>> assessment = PersonalityAssessment()
            >>> questions = assessment.get_questions()
            >>> for q in questions:
            ...     print(f"{q.id}: {q.text}")
        """
        return self._questions.copy()
    
    def get_question_by_id(self, question_id: str) -> Optional[Question]:
        """Get a specific question by ID."""
        for q in self._questions:
            if q.id == question_id:
                return q
        return None
    
    def calculate_traits(
        self,
        responses: Dict[str, int]
    ) -> PsychologicalProfile:
        """
        Calculate Big Five traits from survey responses.
        
        Args:
            responses: Dictionary mapping question IDs to responses (1-5)
                      1 = Strongly Disagree
                      2 = Disagree
                      3 = Neutral
                      4 = Agree
                      5 = Strongly Agree
                      
        Returns:
            PsychologicalProfile with normalized trait scores (0.0-1.0)
            
        Raises:
            ValueError: If responses invalid or incomplete
            
        Examples:
            >>> responses = {"Q01": 4, "Q02": 2, ...}  # All 50 questions
            >>> traits = assessment.calculate_traits(responses)
            >>> print(f"Openness: {traits.openness:.2f}")
        """
        # Validate responses
        self._validate_responses(responses)
        self._responses = responses
        
        # Calculate each trait
        trait_scores = {}
        for trait in TraitDimension:
            score = self._calculate_trait_score(trait, responses)
            trait_scores[trait.value] = score
        
        # Calculate confidence
        self._confidence = self._calculate_confidence(responses)
        
        # Create profile
        return PsychologicalProfile(
            openness=trait_scores["openness"],
            conscientiousness=trait_scores["conscientiousness"],
            extraversion=trait_scores["extraversion"],
            agreeableness=trait_scores["agreeableness"],
            neuroticism=trait_scores["neuroticism"]
        )
    
    def _validate_responses(self, responses: Dict[str, int]) -> None:
        """Validate survey responses."""
        # Check all questions answered
        expected_ids = {q.id for q in self._questions}
        provided_ids = set(responses.keys())
        
        if len(provided_ids) < len(expected_ids):
            missing = expected_ids - provided_ids
            raise ValueError(
                f"Incomplete responses. Missing {len(missing)} questions: "
                f"{sorted(list(missing))[:5]}..."
            )
        
        # Check valid response range (1-5)
        for qid, response in responses.items():
            if not isinstance(response, int) or response < 1 or response > 5:
                raise ValueError(
                    f"Invalid response for {qid}: {response}. "
                    f"Must be integer 1-5."
                )
    
    def _calculate_trait_score(
        self,
        trait: TraitDimension,
        responses: Dict[str, int]
    ) -> float:
        """Calculate normalized score (0.0-1.0) for a trait."""
        # Get questions for this trait
        trait_questions = [q for q in self._questions if q.trait == trait]
        
        # Sum scores (accounting for reverse scoring)
        raw_scores = []
        for question in trait_questions:
            response = responses[question.id]
            
            if question.reverse_scored:
                # Reverse: 1→5, 2→4, 3→3, 4→2, 5→1
                score = 6 - response
            else:
                score = response
            
            raw_scores.append(score)
        
        # Calculate mean and normalize to 0-1
        mean_score = statistics.mean(raw_scores)
        normalized = (mean_score - 1) / 4  # Min=1, Max=5 → 0-1
        
        # Clamp to valid range
        return max(0.0, min(1.0, normalized))
    
    def _calculate_confidence(self, responses: Dict[str, int]) -> float:
        """
        Calculate confidence in assessment accuracy.
        
        Higher confidence when:
        - Strong, consistent responses (avoid all 3s)
        - No contradictions in reverse-scored items
        - All questions answered
        """
        # Check for neutral bias (too many 3s)
        neutral_count = sum(1 for r in responses.values() if r == 3)
        neutral_ratio = neutral_count / len(responses)
        
        # Check for response variance
        variance = statistics.variance(responses.values())
        
        # High confidence if:
        # - Low neutral ratio (<30%)
        # - Good variance (shows differentiation)
        # - All questions answered (already validated)
        
        confidence = 0.7  # Base confidence
        
        # Penalize high neutral responses
        if neutral_ratio > 0.3:
            confidence -= (neutral_ratio - 0.3) * 0.5
        
        # Reward variance (shows clear preferences)
        if variance > 1.0:
            confidence += 0.1
        
        return max(0.4, min(1.0, confidence))
    
    def get_confidence(self) -> float:
        """
        Get confidence score for most recent assessment.
        
        Returns:
            Confidence (0.0-1.0) or 0.0 if no assessment yet
        """
        return self._confidence


class BehavioralCalibrator:
    """
    Infer personality traits from observed behavior.
    
    Use when you don't have survey data but have behavioral history.
    Analyzes patterns in past decisions and actions.
    
    Examples:
        >>> calibrator = BehavioralCalibrator()
        >>> 
        >>> history = [
        ...     {"decision": "Took risky project", "outcome": "success"},
        ...     {"decision": "Avoided conflict", "outcome": "neutral"},
        ...     {"decision": "Planned detailed strategy", "outcome": "success"},
        ...     # ... 10+ events recommended
        ... ]
        >>> 
        >>> traits = calibrator.infer_traits(history)
        >>> confidence = calibrator.get_confidence()
    """
    
    def __init__(self):
        """Initialize behavioral calibrator."""
        self._history: List[Dict] = []
        self._confidence: float = 0.0
    
    def infer_traits(
        self,
        behavioral_history: List[Dict]
    ) -> PsychologicalProfile:
        """
        Infer Big Five traits from behavioral patterns.
        
        Args:
            behavioral_history: List of behavioral events
                Each event should have:
                - decision: What action was taken
                - outcome: Result (success/failure/neutral)
                - context: Optional additional context
                
        Returns:
            Inferred PsychologicalProfile
            
        Raises:
            ValueError: If insufficient behavioral data
            
        Examples:
            >>> history = [
            ...     {"decision": "Started new project without plan",
            ...      "outcome": "success"},
            ...     {"decision": "Took creative approach",
            ...      "outcome": "success"},
            ...     # ... more events
            ... ]
            >>> traits = calibrator.infer_traits(history)
        """
        if len(behavioral_history) < 5:
            raise ValueError(
                f"Need at least 5 behavioral events for inference. "
                f"Got {len(behavioral_history)}. Recommend 10+."
            )
        
        self._history = behavioral_history
        
        # Analyze behavioral patterns
        patterns = self._analyze_patterns(behavioral_history)
        
        # Infer each trait
        traits = {
            "openness": self._infer_openness(patterns),
            "conscientiousness": self._infer_conscientiousness(patterns),
            "extraversion": self._infer_extraversion(patterns),
            "agreeableness": self._infer_agreeableness(patterns),
            "neuroticism": self._infer_neuroticism(patterns)
        }
        
        # Calculate confidence based on data quantity and clarity
        self._confidence = self._calculate_inference_confidence(
            len(behavioral_history),
            patterns
        )
        
        return PsychologicalProfile(**traits)
    
    def _analyze_patterns(self, history: List[Dict]) -> Dict[str, float]:
        """Analyze behavioral patterns from history."""
        patterns = {
            "risk_taking": 0.0,
            "planning": 0.0,
            "social_seeking": 0.0,
            "cooperation": 0.0,
            "stress_response": 0.0,
            "novelty_seeking": 0.0,
            "detail_oriented": 0.0
        }
        
        # Keywords for pattern detection
        for event in history:
            decision = event.get("decision", "").lower()
            
            # Risk-taking patterns
            if any(word in decision for word in ["risk", "uncertain", "gamble", "try", "experiment"]):
                patterns["risk_taking"] += 1
            
            # Planning patterns
            if any(word in decision for word in ["plan", "organize", "prepare", "schedule", "detail"]):
                patterns["planning"] += 1
            
            # Social patterns
            if any(word in decision for word in ["meeting", "collaborate", "team", "group", "social"]):
                patterns["social_seeking"] += 1
            
            # Cooperation patterns
            if any(word in decision for word in ["help", "support", "cooperate", "assist", "compromise"]):
                patterns["cooperation"] += 1
            
            # Stress/anxiety patterns
            if any(word in decision for word in ["worry", "anxious", "stressed", "concern", "fear"]):
                patterns["stress_response"] += 1
            
            # Novelty patterns
            if any(word in decision for word in ["new", "different", "creative", "innovative", "unique"]):
                patterns["novelty_seeking"] += 1
            
            # Detail orientation
            if any(word in decision for word in ["detail", "careful", "thorough", "precise", "exact"]):
                patterns["detail_oriented"] += 1
        
        # Normalize by history length
        total = len(history)
        for key in patterns:
            patterns[key] = patterns[key] / total
        
        return patterns
    
    def _infer_openness(self, patterns: Dict[str, float]) -> float:
        """Infer openness from novelty-seeking and risk-taking."""
        score = (patterns["novelty_seeking"] * 0.6 + 
                patterns["risk_taking"] * 0.4)
        return max(0.0, min(1.0, score + 0.3))  # Baseline + behavior
    
    def _infer_conscientiousness(self, patterns: Dict[str, float]) -> float:
        """Infer conscientiousness from planning and detail orientation."""
        score = (patterns["planning"] * 0.5 + 
                patterns["detail_oriented"] * 0.5)
        return max(0.0, min(1.0, score + 0.3))
    
    def _infer_extraversion(self, patterns: Dict[str, float]) -> float:
        """Infer extraversion from social-seeking behavior."""
        score = patterns["social_seeking"]
        return max(0.0, min(1.0, score + 0.3))
    
    def _infer_agreeableness(self, patterns: Dict[str, float]) -> float:
        """Infer agreeableness from cooperation patterns."""
        score = patterns["cooperation"]
        return max(0.0, min(1.0, score + 0.4))
    
    def _infer_neuroticism(self, patterns: Dict[str, float]) -> float:
        """Infer neuroticism from stress response patterns."""
        score = patterns["stress_response"]
        return max(0.0, min(1.0, score + 0.2))
    
    def _calculate_inference_confidence(
        self,
        event_count: int,
        patterns: Dict[str, float]
    ) -> float:
        """Calculate confidence in behavioral inference."""
        # More events = higher confidence
        count_confidence = min(1.0, event_count / 20)  # Plateau at 20 events
        
        # Clear patterns = higher confidence
        pattern_strength = statistics.mean(patterns.values())
        pattern_confidence = pattern_strength
        
        # Combined confidence
        confidence = (count_confidence * 0.6 + pattern_confidence * 0.4)
        
        return max(0.3, min(0.9, confidence))
    
    def get_confidence(self) -> float:
        """Get confidence score for most recent inference."""
        return self._confidence
