# src/simulacrum/digital_twin/team.py
"""
Team Digital Twin for simulating group dynamics and team decisions.

This module enables simulation of team interactions, group decision-making,
conflict prediction, and collaboration optimization.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .twin import DigitalTwin, Decision


class VotingMethod(Enum):
    """Methods for team decision-making."""
    MAJORITY = "majority"          # Simple majority wins
    CONSENSUS = "consensus"        # Require broad agreement
    UNANIMOUS = "unanimous"        # Everyone must agree
    WEIGHTED = "weighted"          # Based on expertise/role


@dataclass
class TeamDecision:
    """
    Result of a team decision-making process.
    
    Attributes:
        outcome: Final decision ("Accept", "Decline", etc.)
        voting_method: How the decision was made
        individual_votes: How each member voted
        consensus_strength: How unified the team was (0.0-1.0)
        conflicts: Predicted conflicts between members
        reasoning: Natural language explanation
        timestamp: When decision was made
    """
    outcome: str
    voting_method: VotingMethod
    individual_votes: Dict[str, str]
    consensus_strength: float
    conflicts: List["Conflict"] = field(default_factory=list)
    reasoning: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "outcome": self.outcome,
            "voting_method": self.voting_method.value,
            "individual_votes": self.individual_votes,
            "consensus_strength": self.consensus_strength,
            "conflicts": [c.to_dict() for c in self.conflicts],
            "reasoning": self.reasoning,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class Conflict:
    """
    Predicted conflict between team members.
    
    Attributes:
        between: Names of conflicting members
        reason: Why they disagree
        severity: How serious (0.0-1.0)
        trait_differences: Which personality differences cause conflict
    """
    between: List[str]
    reason: str
    severity: float
    trait_differences: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "between": self.between,
            "reason": self.reason,
            "severity": self.severity,
            "trait_differences": self.trait_differences
        }


class TeamDigitalTwin:
    """
    Digital twin of a team for simulating group dynamics.
    
    Aggregates individual digital twins to model team behavior,
    predict conflicts, and simulate collective decision-making.
    
    Examples:
        >>> # Create team from individual twins
        >>> team = TeamDigitalTwin([alice_twin, bob_twin, carol_twin])
        >>> 
        >>> # Simulate team decision
        >>> decision = team.simulate_team_decision(
        ...     "Launch AI feature at $25K cost?",
        ...     voting_method="consensus"
        ... )
        >>> 
        >>> print(decision.outcome)           # "Accept" or "Decline"
        >>> print(decision.consensus_strength) # 0.85
        >>> print(len(decision.conflicts))    # 1 predicted conflict
    """
    
    def __init__(
        self,
        members: List[DigitalTwin],
        name: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Initialize team digital twin.
        
        Args:
            members: List of individual digital twins
            name: Optional team name
            metadata: Optional team metadata (roles, structure, etc.)
            
        Raises:
            ValueError: If members list is empty or has < 2 members
        """
        if not members:
            raise ValueError("Team must have at least one member")
        
        if len(members) < 2:
            raise ValueError(
                f"Team must have at least 2 members for group dynamics. "
                f"Got {len(members)}. For individual decisions, use DigitalTwin directly."
            )
        
        self.members = members
        self.name = name or f"Team of {len(members)}"
        self.metadata = metadata or {}
        self._decision_history: List[TeamDecision] = []
        self._created_at = datetime.now()
    
    def simulate_team_decision(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        voting_method: str = "majority",
        require_threshold: float = 0.5
    ) -> TeamDecision:
        """
        Simulate how the team would make a decision.
        
        Args:
            question: Decision to make
            context: Additional context
            voting_method: "majority", "consensus", "unanimous", or "weighted"
            require_threshold: Threshold for consensus/weighted (0.0-1.0)
            
        Returns:
            TeamDecision with outcome and analysis
            
        Examples:
            >>> decision = team.simulate_team_decision(
            ...     "Launch product now or wait 2 months?",
            ...     context={"budget": 100000, "readiness": "70%"},
            ...     voting_method="consensus"
            ... )
            >>> 
            >>> print(f"Decision: {decision.outcome}")
            >>> print(f"Consensus: {decision.consensus_strength:.0%}")
            >>> for conflict in decision.conflicts:
            ...     print(f"Conflict: {conflict.reason}")
        """
        # Convert voting_method string to enum
        try:
            method = VotingMethod(voting_method.lower())
        except ValueError:
            raise ValueError(
                f"Invalid voting_method: {voting_method}. "
                f"Must be one of: {[m.value for m in VotingMethod]}"
            )
        
        # Get individual decisions from each member
        individual_decisions = self._get_individual_decisions(question, context)
        
        # Calculate team outcome based on voting method
        outcome = self._calculate_outcome(
            individual_decisions,
            method,
            require_threshold
        )
        
        # Calculate consensus strength
        consensus_strength = self._calculate_consensus(individual_decisions)
        
        # Predict conflicts
        conflicts = self.predict_conflicts(question, context, individual_decisions)
        
        # Generate team reasoning
        reasoning = self._generate_team_reasoning(
            individual_decisions,
            outcome,
            conflicts
        )
        
        # Create team decision
        decision = TeamDecision(
            outcome=outcome,
            voting_method=method,
            individual_votes={d["member"]: d["recommendation"] 
                            for d in individual_decisions},
            consensus_strength=consensus_strength,
            conflicts=conflicts,
            reasoning=reasoning
        )
        
        # Store in history
        self._decision_history.append(decision)
        
        return decision
    
    def predict_conflicts(
        self,
        scenario: str,
        context: Optional[Dict[str, Any]] = None,
        individual_decisions: Optional[List[Dict]] = None
    ) -> List[Conflict]:
        """
        Predict conflicts within the team for a scenario.
        
        Args:
            scenario: Situation to analyze
            context: Additional context
            individual_decisions: Pre-computed decisions (optional)
            
        Returns:
            List of predicted Conflict objects
            
        Examples:
            >>> conflicts = team.predict_conflicts(
            ...     "Restructure team into new roles",
            ...     context={"timeline": "immediate"}
            ... )
            >>> 
            >>> for conflict in conflicts:
            ...     print(f"{' vs '.join(conflict.between)}: {conflict.reason}")
        """
        # Get individual decisions if not provided
        if individual_decisions is None:
            individual_decisions = self._get_individual_decisions(scenario, context)
        
        conflicts = []
        
        # Compare each pair of members
        for i, decision1 in enumerate(individual_decisions):
            for decision2 in individual_decisions[i+1:]:
                # Check if they disagree
                if decision1["recommendation"] != decision2["recommendation"]:
                    # Analyze personality differences
                    member1 = self._get_member_by_name(decision1["member"])
                    member2 = self._get_member_by_name(decision2["member"])
                    
                    trait_diffs = self._calculate_trait_differences(
                        member1.traits,
                        member2.traits
                    )
                    
                    # Determine severity based on decision confidence + trait differences
                    severity = (
                        decision1["confidence"] * decision2["confidence"] * 0.6 +
                        max(trait_diffs.values()) * 0.4
                    )
                    
                    # Generate conflict reason
                    reason = self._generate_conflict_reason(
                        decision1,
                        decision2,
                        trait_diffs
                    )
                    
                    conflict = Conflict(
                        between=[decision1["member"], decision2["member"]],
                        reason=reason,
                        severity=severity,
                        trait_differences=trait_diffs
                    )
                    
                    conflicts.append(conflict)
        
        # Sort by severity (highest first)
        conflicts.sort(key=lambda c: c.severity, reverse=True)
        
        return conflicts
    
    def get_team_composition(self) -> Dict[str, Any]:
        """
        Get analysis of team personality composition.
        
        Returns:
            Dictionary with team statistics and diversity metrics
            
        Examples:
            >>> composition = team.get_team_composition()
            >>> print(f"Average openness: {composition['avg_traits']['openness']:.2f}")
            >>> print(f"Diversity score: {composition['diversity_score']:.2f}")
        """
        # Calculate average traits
        avg_traits = {
            "openness": sum(m.traits.openness for m in self.members) / len(self.members),
            "conscientiousness": sum(m.traits.conscientiousness for m in self.members) / len(self.members),
            "extraversion": sum(m.traits.extraversion for m in self.members) / len(self.members),
            "agreeableness": sum(m.traits.agreeableness for m in self.members) / len(self.members),
            "neuroticism": sum(m.traits.neuroticism for m in self.members) / len(self.members)
        }
        
        # Calculate diversity (variance in traits)
        import statistics
        diversity_scores = []
        for trait in avg_traits.keys():
            values = [getattr(m.traits, trait) for m in self.members]
            if len(values) > 1:
                diversity_scores.append(statistics.variance(values))
        
        diversity_score = sum(diversity_scores) / len(diversity_scores) if diversity_scores else 0
        
        return {
            "size": len(self.members),
            "members": [m.name for m in self.members],
            "avg_traits": avg_traits,
            "diversity_score": diversity_score,
            "high_traits": [trait for trait, value in avg_traits.items() if value > 0.6],
            "low_traits": [trait for trait, value in avg_traits.items() if value < 0.4]
        }
    
    def optimize_collaboration(self) -> Dict[str, Any]:
        """
        Get recommendations for optimizing team collaboration.
        
        Returns:
            Dictionary with recommendations based on team composition
            
        Examples:
            >>> recs = team.optimize_collaboration()
            >>> for rec in recs['recommendations']:
            ...     print(f"- {rec}")
        """
        composition = self.get_team_composition()
        recommendations = []
        
        # Check for low agreeableness
        if composition["avg_traits"]["agreeableness"] < 0.4:
            recommendations.append(
                "Team has low agreeableness - establish clear conflict resolution processes"
            )
        
        # Check for high neuroticism
        if composition["avg_traits"]["neuroticism"] > 0.6:
            recommendations.append(
                "Team has high stress sensitivity - provide psychological safety and support"
            )
        
        # Check for low diversity
        if composition["diversity_score"] < 0.1:
            recommendations.append(
                "Team lacks personality diversity - consider diverse perspectives in hiring"
            )
        
        # Check for high diversity
        if composition["diversity_score"] > 0.3:
            recommendations.append(
                "Team has high diversity - leverage different perspectives but ensure alignment"
            )
        
        # Check for extreme introversion
        if composition["avg_traits"]["extraversion"] < 0.3:
            recommendations.append(
                "Team is highly introverted - provide async communication channels and quiet time"
            )
        
        # Check for extreme extraversion
        if composition["avg_traits"]["extraversion"] > 0.7:
            recommendations.append(
                "Team is highly extraverted - provide collaboration spaces and social activities"
            )
        
        return {
            "composition": composition,
            "recommendations": recommendations if recommendations else ["Team composition is well-balanced"]
        }
    
    def get_decision_history(self, limit: Optional[int] = None) -> List[TeamDecision]:
        """Get history of team decisions."""
        history = sorted(
            self._decision_history,
            key=lambda d: d.timestamp,
            reverse=True
        )
        
        if limit:
            return history[:limit]
        return history
    
    # Private methods
    
    def _get_individual_decisions(
        self,
        question: str,
        context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Get decision from each team member."""
        decisions = []
        
        for member in self.members:
            decision = member.simulate_decision(
                question,
                context,
                use_memory=True
            )
            
            decisions.append({
                "member": member.name,
                "recommendation": decision.recommendation,
                "reasoning": decision.reasoning,
                "confidence": decision.confidence,
                "personality_factors": decision.personality_factors
            })
        
        return decisions
    
    def _calculate_outcome(
        self,
        individual_decisions: List[Dict],
        method: VotingMethod,
        threshold: float
    ) -> str:
        """Calculate team outcome based on voting method."""
        recommendations = [d["recommendation"] for d in individual_decisions]
        
        if method == VotingMethod.MAJORITY:
            # Simple majority
            from collections import Counter
            counts = Counter(recommendations)
            return counts.most_common(1)[0][0]
        
        elif method == VotingMethod.CONSENSUS:
            # Require threshold agreement
            from collections import Counter
            counts = Counter(recommendations)
            most_common = counts.most_common(1)[0]
            
            if most_common[1] / len(recommendations) >= threshold:
                return most_common[0]
            else:
                return "No Consensus"
        
        elif method == VotingMethod.UNANIMOUS:
            # Everyone must agree
            if len(set(recommendations)) == 1:
                return recommendations[0]
            else:
                return "No Agreement"
        
        elif method == VotingMethod.WEIGHTED:
            # Weight by confidence
            weighted_votes = {}
            for decision in individual_decisions:
                rec = decision["recommendation"]
                conf = decision["confidence"]
                weighted_votes[rec] = weighted_votes.get(rec, 0) + conf
            
            return max(weighted_votes.items(), key=lambda x: x[1])[0]
        
        return "Unknown"
    
    def _calculate_consensus(self, individual_decisions: List[Dict]) -> float:
        """Calculate consensus strength (0.0-1.0)."""
        recommendations = [d["recommendation"] for d in individual_decisions]
        
        from collections import Counter
        counts = Counter(recommendations)
        most_common_count = counts.most_common(1)[0][1]
        
        # Consensus = proportion agreeing with most common
        consensus = most_common_count / len(recommendations)
        
        return consensus
    
    def _get_member_by_name(self, name: str) -> DigitalTwin:
        """Get team member by name."""
        for member in self.members:
            if member.name == name:
                return member
        raise ValueError(f"Member not found: {name}")
    
    def _calculate_trait_differences(self, traits1, traits2) -> Dict[str, float]:
        """Calculate absolute differences in personality traits."""
        return {
            "openness": abs(traits1.openness - traits2.openness),
            "conscientiousness": abs(traits1.conscientiousness - traits2.conscientiousness),
            "extraversion": abs(traits1.extraversion - traits2.extraversion),
            "agreeableness": abs(traits1.agreeableness - traits2.agreeableness),
            "neuroticism": abs(traits1.neuroticism - traits2.neuroticism)
        }
    
    def _generate_conflict_reason(
        self,
        decision1: Dict,
        decision2: Dict,
        trait_diffs: Dict[str, float]
    ) -> str:
        """Generate explanation for why members conflict."""
        # Find largest trait difference
        max_diff_trait = max(trait_diffs.items(), key=lambda x: x[1])
        
        reasons = {
            "openness": f"{decision1['member']} and {decision2['member']} differ on innovation vs tradition",
            "conscientiousness": f"{decision1['member']} prefers planning while {decision2['member']} prefers flexibility",
            "extraversion": f"{decision1['member']} and {decision2['member']} have different communication styles",
            "agreeableness": f"{decision1['member']} and {decision2['member']} approach collaboration differently",
            "neuroticism": f"{decision1['member']} and {decision2['member']} have different risk tolerances"
        }
        
        return reasons.get(max_diff_trait[0], "Personality differences")
    
    def _generate_team_reasoning(
        self,
        individual_decisions: List[Dict],
        outcome: str,
        conflicts: List[Conflict]
    ) -> str:
        """Generate natural language explanation of team decision."""
        # Count recommendations
        from collections import Counter
        counts = Counter([d["recommendation"] for d in individual_decisions])
        
        # Build reasoning
        reasoning_parts = []
        
        # Overall outcome
        if outcome in counts:
            supporting = counts[outcome]
            reasoning_parts.append(
                f"Team decided to {outcome} with {supporting}/{len(individual_decisions)} members in favor."
            )
        
        # Mention conflicts if any
        if conflicts:
            reasoning_parts.append(
                f"There were {len(conflicts)} predicted conflicts, "
                f"particularly between {' and '.join(conflicts[0].between)}."
            )
        else:
            reasoning_parts.append("Team showed strong alignment with no major conflicts.")
        
        return " ".join(reasoning_parts)
   
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"TeamDigitalTwin(name='{self.name}', "
            f"members={len(self.members)}, "
            f"decisions={len(self._decision_history)})"
        )
