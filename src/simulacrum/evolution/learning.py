# src/simulacrum/evolution/learning.py
"""
Learning and adaptation systems for agents.

Agents learn from:
- Outcomes of their decisions
- Feedback from environment
- Observation of other agents
- Repeated experiences
"""

from typing import List, Dict, Any, Optional, Callable
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
import statistics


class OutcomeType(str, Enum):
    """Types of outcomes from decisions."""
    SUCCESS = "success"
    FAILURE = "failure"
    MIXED = "mixed"


class Decision(BaseModel):
    """A decision made by an agent."""
    id: str
    timestamp: datetime
    context: str
    choice: str
    reasoning: str = ""
    confidence: float = 0.5


class Outcome(BaseModel):
    """The outcome of a decision."""
    decision_id: str
    timestamp: datetime
    outcome_type: OutcomeType
    reward: float = 0.0  # Positive or negative
    feedback: str = ""


class Strategy(BaseModel):
    """A learned strategy for a type of situation."""
    context_type: str
    description: str
    success_rate: float = 0.0
    times_used: int = 0
    total_reward: float = 0.0
    last_used: Optional[datetime] = None


class AdaptiveLearner:
    """
    Enables agents to learn from experience and adapt behavior.
    
    Learning mechanisms:
    - Reinforcement: Successful strategies used more
    - Punishment: Failed strategies avoided
    - Generalization: Lessons applied to similar situations
    - Observation: Learn from others' outcomes
    """
    
    def __init__(self, agent: Any, learning_rate: float = 0.1):
        """
        Initialize learning system.
        
        Args:
            agent: The agent who will learn
            learning_rate: How quickly to update from feedback (0.0-1.0)
        """
        self.agent = agent
        self.learning_rate = learning_rate
        
        # Track decisions and outcomes
        self.decisions: List[Decision] = []
        self.outcomes: List[Outcome] = []
        
        # Learned strategies
        self.strategies: Dict[str, Strategy] = {}
        
        # Performance tracking
        self.success_count = 0
        self.failure_count = 0
    
    def record_decision(
        self,
        context: str,
        choice: str,
        reasoning: str = "",
        confidence: float = 0.5
    ) -> Decision:
        """Record a decision for future learning."""
        decision = Decision(
            id=f"dec_{len(self.decisions)+1}",
            timestamp=datetime.now(),
            context=context,
            choice=choice,
            reasoning=reasoning,
            confidence=confidence
        )
        
        self.decisions.append(decision)
        return decision
    
    def record_outcome(
        self,
        decision_id: str,
        outcome_type: OutcomeType,
        reward: float = 0.0,
        feedback: str = ""
    ) -> Outcome:
        """
        Record outcome and learn from it.
        
        This updates strategies and may affect personality traits.
        """
        outcome = Outcome(
            decision_id=decision_id,
            timestamp=datetime.now(),
            outcome_type=outcome_type,
            reward=reward,
            feedback=feedback
        )
        
        self.outcomes.append(outcome)
        
        # Update performance counters
        if outcome_type == OutcomeType.SUCCESS:
            self.success_count += 1
        elif outcome_type == OutcomeType.FAILURE:
            self.failure_count += 1
        
        # Learn from outcome
        self._learn_from_outcome(decision_id, outcome)
        
        return outcome
    
    def _learn_from_outcome(self, decision_id: str, outcome: Outcome):
        """Update strategies based on outcome."""
        # Find the decision
        decision = next(
            (d for d in self.decisions if d.id == decision_id),
            None
        )
        
        if not decision:
            return
        
        # Update or create strategy for this context
        strategy_key = f"{decision.context}:{decision.choice}"
        
        if strategy_key not in self.strategies:
            self.strategies[strategy_key] = Strategy(
                context_type=decision.context,
                description=f"Choose '{decision.choice}' in {decision.context}"
            )
        
        strategy = self.strategies[strategy_key]
        
        # Update strategy statistics
        strategy.times_used += 1
        strategy.total_reward += outcome.reward
        strategy.last_used = datetime.now()
        
        # Update success rate
        if outcome.outcome_type == OutcomeType.SUCCESS:
            strategy.success_rate = (
                (strategy.success_rate * (strategy.times_used - 1) + 1.0) 
                / strategy.times_used
            )
        elif outcome.outcome_type == OutcomeType.FAILURE:
            strategy.success_rate = (
                (strategy.success_rate * (strategy.times_used - 1) + 0.0) 
                / strategy.times_used
            )
        else:  # Mixed
            strategy.success_rate = (
                (strategy.success_rate * (strategy.times_used - 1) + 0.5) 
                / strategy.times_used
            )
    
    def get_best_strategy(self, context: str) -> Optional[Strategy]:
        """
        Get the best learned strategy for a context.
        
        "Best" is determined by success rate and total reward.
        """
        relevant_strategies = [
            s for s in self.strategies.values()
            if s.context_type == context and s.times_used > 0
        ]
        
        if not relevant_strategies:
            return None
        
        # Weight by both success rate and average reward
        def score(s: Strategy):
            avg_reward = s.total_reward / s.times_used if s.times_used > 0 else 0
            return s.success_rate * 0.7 + (avg_reward / 100) * 0.3
        
        return max(relevant_strategies, key=score)
    
    def should_explore(self) -> bool:
        """
        Decide whether to explore (try new things) or exploit (use best known).
        
        Higher openness → more exploration
        More failures recently → more exploration
        """
        # Base exploration rate from openness
        exploration_rate = self.agent.traits.openness * 0.3
        
        # If recent performance is poor, explore more
        recent_decisions = self.decisions[-10:]
        recent_outcomes = [
            o for o in self.outcomes
            if any(o.decision_id == d.id for d in recent_decisions)
        ]
        
        if recent_outcomes:
            recent_success_rate = sum(
                1 for o in recent_outcomes 
                if o.outcome_type == OutcomeType.SUCCESS
            ) / len(recent_outcomes)
            
            # Poor performance → increase exploration
            if recent_success_rate < 0.4:
                exploration_rate += 0.2
        
        # Random exploration decision
        import random
        return random.random() < exploration_rate
    
    def learn_from_observation(
        self,
        other_agent: 'AdaptiveLearner',
        context: str
    ):
        """
        Learn from observing another agent's experiences.
        
        Vicarious learning: observe others' outcomes and adopt their strategies.
        """
        # Find successful strategies from other agent in this context
        other_strategies = [
            s for s in other_agent.strategies.values()
            if s.context_type == context and s.success_rate > 0.6
        ]
        
        for strategy in other_strategies:
            strategy_key = f"{strategy.context_type}:{strategy.description}"
            
            # If we don't have this strategy, adopt it (with reduced confidence)
            if strategy_key not in self.strategies:
                self.strategies[strategy_key] = Strategy(
                    context_type=strategy.context_type,
                    description=strategy.description,
                    success_rate=strategy.success_rate * 0.7,  # Discount observed success
                    times_used=0
                )
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of learning performance."""
        total_decisions = len(self.decisions)
        total_rewards = sum(o.reward for o in self.outcomes)
        
        if total_decisions == 0:
            return {
                "total_decisions": 0,
                "success_rate": 0.0,
                "average_reward": 0.0,
                "strategies_learned": 0
            }
        
        return {
            "total_decisions": total_decisions,
            "success_rate": self.success_count / total_decisions if total_decisions > 0 else 0.0,
            "average_reward": total_rewards / total_decisions if total_decisions > 0 else 0.0,
            "strategies_learned": len(self.strategies),
            "best_strategy": self._get_best_overall_strategy()
        }
    
    def _get_best_overall_strategy(self) -> Optional[Dict[str, Any]]:
        """Get the single best strategy across all contexts."""
        if not self.strategies:
            return None
        
        best = max(
            self.strategies.values(),
            key=lambda s: s.success_rate * (s.times_used ** 0.5)  # Balance success and experience
        )
        
        return {
            "context": best.context_type,
            "description": best.description,
            "success_rate": round(best.success_rate, 2),
            "times_used": best.times_used,
            "avg_reward": round(best.total_reward / best.times_used, 2) if best.times_used > 0 else 0
        }


class PopulationLearning:
    """
    Track learning across a population of agents.
    
    Shows emergence of:
    - Collective knowledge
    - Cultural transmission
    - Strategy convergence or divergence
    """
    
    def __init__(self, learners: List[AdaptiveLearner]):
        self.learners = learners
        self.generation = 0
    
    def share_knowledge(self, interaction_probability: float = 0.3):
        """
        Agents randomly interact and share learned strategies.
        
        Models cultural transmission of knowledge.
        """
        import random
        
        for learner in self.learners:
            if random.random() < interaction_probability:
                # Pick another agent to observe
                other = random.choice(
                    [l for l in self.learners if l != learner]
                )
                
                # Share knowledge about all contexts
                contexts = set(
                    s.context_type 
                    for s in other.strategies.values()
                )
                
                for context in contexts:
                    learner.learn_from_observation(other, context)
    
    def get_population_statistics(self) -> Dict[str, Any]:
        """Analyze learning across the population."""
        if not self.learners:
            return {}
        
        total_strategies = sum(len(l.strategies) for l in self.learners)
        avg_success_rate = statistics.mean(
            l.success_count / max(len(l.decisions), 1)
            for l in self.learners
        )
        
        # Find most common successful strategies
        strategy_usage = {}
        for learner in self.learners:
            for key, strategy in learner.strategies.items():
                if strategy.success_rate > 0.6:
                    if key not in strategy_usage:
                        strategy_usage[key] = {
                            "count": 0,
                            "avg_success": 0.0,
                            "description": strategy.description
                        }
                    strategy_usage[key]["count"] += 1
                    strategy_usage[key]["avg_success"] += strategy.success_rate
        
        # Get top 3 shared strategies
        top_strategies = sorted(
            strategy_usage.items(),
            key=lambda x: (x[1]["count"], x[1]["avg_success"]),
            reverse=True
        )[:3]
        
        return {
            "population_size": len(self.learners),
            "total_strategies": total_strategies,
            "avg_strategies_per_agent": round(total_strategies / len(self.learners), 1),
            "population_success_rate": round(avg_success_rate, 2),
            "shared_strategies": [
                {
                    "description": s[1]["description"],
                    "adoption": s[1]["count"],
                    "avg_success": round(s[1]["avg_success"] / s[1]["count"], 2)
                }
                for s in top_strategies
            ]
        }


def create_adaptive_learner(
    agent: Any,
    learning_rate: float = 0.1
) -> AdaptiveLearner:
    """
    Add learning capabilities to an agent.
    
    Example:
        agent = create_early_adopter()
        learner = create_adaptive_learner(agent, learning_rate=0.15)
        
        # Make decision
        decision = learner.record_decision("pricing", "increase_by_10%")
        
        # Observe outcome
        learner.record_outcome(decision.id, OutcomeType.SUCCESS, reward=500)
        
        # Next time, use learned strategy
        best = learner.get_best_strategy("pricing")
    """
    return AdaptiveLearner(agent, learning_rate)
