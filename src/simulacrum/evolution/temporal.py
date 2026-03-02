# src/simulacrum/evolution/temporal.py
"""
Temporal dynamics for agents: memory decay, trait evolution, and behavioral drift.

Models how agents change over time through:
- Experience accumulation
- Memory decay and reinforcement
- Trait adaptation based on outcomes
- Social influence
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from enum import Enum
import statistics


class ExperienceType(str, Enum):
    """Types of experiences that shape agents."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class Experience(BaseModel):
    """A significant experience that affects the agent."""
    id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    type: ExperienceType
    description: str
    context: str = ""
    intensity: float = 1.0  # 0.0-1.0, how impactful
    trait_impacts: Dict[str, float] = {}  # Which traits affected and by how much


class TraitEvolution(BaseModel):
    """Records how a trait has evolved over time."""
    trait_name: str
    initial_value: float
    current_value: float
    history: List[tuple[datetime, float]] = []  # Timestamp, value pairs
    total_drift: float = 0.0


class TemporalAgent:
    """
    Adds temporal dynamics to agents.
    
    Capabilities:
    - Experience tracking
    - Memory decay
    - Trait evolution
    - Behavioral drift monitoring
    """
    
    def __init__(self, base_agent: Any, drift_rate: float = 0.01):
        """
        Initialize temporal capabilities.
        
        Args:
            base_agent: The citizen agent to add temporal dynamics to
            drift_rate: How quickly traits can change (0.0-1.0)
        """
        self.agent = base_agent
        self.drift_rate = drift_rate
        
        # Track experiences
        self.experiences: List[Experience] = []
        self.experience_count = 0
        
        # Track trait evolution
        self.trait_evolution: Dict[str, TraitEvolution] = {}
        self._initialize_trait_tracking()
        
        # Social influence
        self.social_influences: List[Dict[str, Any]] = []
        
        # Last update time
        self.last_update = datetime.now()
    
    def _initialize_trait_tracking(self):
        """Initialize tracking for all personality traits."""
        traits = {
            "openness": self.agent.traits.openness,
            "conscientiousness": self.agent.traits.conscientiousness,
            "extraversion": self.agent.traits.extraversion,
            "agreeableness": self.agent.traits.agreeableness,
            "neuroticism": self.agent.traits.neuroticism
        }
        
        for trait_name, value in traits.items():
            self.trait_evolution[trait_name] = TraitEvolution(
                trait_name=trait_name,
                initial_value=value,
                current_value=value,
                history=[(datetime.now(), value)]
            )
    
    def add_experience(
        self,
        description: str,
        experience_type: ExperienceType,
        intensity: float = 1.0,
        context: str = "",
        trait_impacts: Optional[Dict[str, float]] = None
    ) -> Experience:
        """
        Add a significant experience that may affect the agent.
        
        Args:
            description: What happened
            experience_type: Positive, negative, or neutral
            intensity: How impactful (0.0-1.0)
            context: Additional context
            trait_impacts: Explicit trait changes (optional)
        """
        self.experience_count += 1
        
        experience = Experience(
            id=f"exp_{self.experience_count}",
            type=experience_type,
            description=description,
            context=context,
            intensity=intensity,
            trait_impacts=trait_impacts or {}
        )
        
        self.experiences.append(experience)
        
        # Apply trait impacts if specified
        if trait_impacts:
            for trait_name, delta in trait_impacts.items():
                self._adjust_trait(trait_name, delta * intensity)
        
        # Store in agent memory
        self.agent.remember(
            f"Experienced: {description} ({experience_type.value})",
            context=context
        )
        
        return experience
    
    def _adjust_trait(self, trait_name: str, delta: float):
        """
        Adjust a personality trait based on experience.
        
        Traits can drift but are constrained to [0, 1].
        """
        if trait_name not in self.trait_evolution:
            return
        
        evolution = self.trait_evolution[trait_name]
        
        # Calculate new value with drift rate
        change = delta * self.drift_rate
        new_value = evolution.current_value + change
        
        # Constrain to valid range
        new_value = max(0.0, min(1.0, new_value))
        
        # Update evolution tracking
        evolution.current_value = new_value
        evolution.total_drift += abs(change)
        evolution.history.append((datetime.now(), new_value))
        
        # Update agent's actual trait
        setattr(self.agent.traits, trait_name, new_value)
    
    def apply_social_influence(
        self,
        influencer: 'TemporalAgent',
        interaction_type: str,
        strength: float = 0.5
    ):
        """
        Agent is influenced by interaction with another agent.
        
        Social influence can shift traits toward the influencer's traits.
        """
        influence_record = {
            "timestamp": datetime.now(),
            "influencer": influencer.agent.name,
            "type": interaction_type,
            "strength": strength
        }
        
        self.social_influences.append(influence_record)
        
        # Calculate trait shifts
        # Agreeableness makes agents more susceptible to influence
        susceptibility = self.agent.traits.agreeableness * strength
        
        for trait_name in self.trait_evolution.keys():
            my_value = getattr(self.agent.traits, trait_name)
            their_value = getattr(influencer.agent.traits, trait_name)
            
            # Shift slightly toward influencer's value
            delta = (their_value - my_value) * susceptibility * 0.1
            self._adjust_trait(trait_name, delta)
    
    def decay_memories(self, days_elapsed: float = 1.0):
        """
        Simulate memory decay over time.
        
        Older memories become less salient unless reinforced.
        """
        decay_rate = 0.1 * days_elapsed  # 10% decay per day
        
        # In a full implementation, we'd mark memories as decayed
        # For now, we just track that decay occurred
        self.agent.remember(
            f"Memory consolidation after {days_elapsed:.1f} days",
            context="Temporal processing"
        )
    
    def get_trait_drift(self, trait_name: str) -> float:
        """Get total drift for a specific trait."""
        if trait_name not in self.trait_evolution:
            return 0.0
        return self.trait_evolution[trait_name].total_drift
    
    def get_trait_history(self, trait_name: str) -> List[tuple[datetime, float]]:
        """Get historical values of a trait."""
        if trait_name not in self.trait_evolution:
            return []
        return self.trait_evolution[trait_name].history.copy()
    
    def summarize_evolution(self) -> Dict[str, Any]:
        """Get summary of how agent has evolved."""
        summary = {
            "experiences": len(self.experiences),
            "social_influences": len(self.social_influences),
            "trait_changes": {}
        }
        
        for trait_name, evolution in self.trait_evolution.items():
            change = evolution.current_value - evolution.initial_value
            summary["trait_changes"][trait_name] = {
                "initial": round(evolution.initial_value, 3),
                "current": round(evolution.current_value, 3),
                "change": round(change, 3),
                "drift": round(evolution.total_drift, 3)
            }
        
        return summary


class LongTermSimulation:
    """
    Framework for simulating agents over extended time periods.
    
    Tracks:
    - Agent evolution
    - Interaction effects
    - Emergent behavioral patterns
    """
    
    def __init__(self, agents: List[TemporalAgent]):
        self.agents = agents
        self.timeline: List[Dict[str, Any]] = []
        self.current_time = datetime.now()
    
    def advance_time(self, days: float = 1.0):
        """Advance simulation time and apply temporal effects."""
        self.current_time += timedelta(days=days)
        
        # Apply memory decay to all agents
        for agent in self.agents:
            agent.decay_memories(days)
    
    def record_event(self, event_type: str, description: str, agents: List[str]):
        """Record a significant event in the timeline."""
        event = {
            "timestamp": self.current_time,
            "type": event_type,
            "description": description,
            "agents": agents
        }
        self.timeline.append(event)
    
    def simulate_interaction(
        self,
        agent1: TemporalAgent,
        agent2: TemporalAgent,
        interaction_type: str = "conversation"
    ):
        """
        Simulate interaction between two agents.
        
        Both agents may influence each other.
        """
        # Mutual influence based on extraversion
        influence_strength_1 = agent1.agent.traits.extraversion
        influence_strength_2 = agent2.agent.traits.extraversion
        
        # Each influences the other
        agent1.apply_social_influence(agent2, interaction_type, influence_strength_2)
        agent2.apply_social_influence(agent1, interaction_type, influence_strength_1)
        
        # Record event
        self.record_event(
            "interaction",
            f"{interaction_type} between agents",
            [agent1.agent.name, agent2.agent.name]
        )
    
    def simulate_market_experience(
        self,
        agent: TemporalAgent,
        success: bool,
        profit: float = 0.0
    ):
        """
        Simulate market trading experience and its effects.
        
        Success increases openness (risk tolerance).
        Failure increases neuroticism (anxiety).
        """
        if success:
            agent.add_experience(
                description=f"Successful trade with ${profit:.0f} profit",
                experience_type=ExperienceType.POSITIVE,
                intensity=min(1.0, abs(profit) / 500),
                context="Market trading",
                trait_impacts={
                    "openness": 0.05,  # More willing to take risks
                    "neuroticism": -0.03  # Less anxious
                }
            )
        else:
            agent.add_experience(
                description=f"Failed trade with ${abs(profit):.0f} loss",
                experience_type=ExperienceType.NEGATIVE,
                intensity=min(1.0, abs(profit) / 500),
                context="Market trading",
                trait_impacts={
                    "neuroticism": 0.05,  # More anxious
                    "openness": -0.02  # More conservative
                }
            )
    
    def get_trait_convergence(self, trait_name: str) -> float:
        """
        Calculate how much agents' traits have converged.
        
        Returns standard deviation (lower = more convergence).
        """
        values = [
            getattr(agent.agent.traits, trait_name)
            for agent in self.agents
        ]
        
        if len(values) < 2:
            return 0.0
        
        return statistics.stdev(values)
    
    def analyze_evolution(self) -> Dict[str, Any]:
        """Analyze how the population has evolved."""
        analysis = {
            "total_experiences": sum(len(a.experiences) for a in self.agents),
            "total_interactions": len([e for e in self.timeline if e["type"] == "interaction"]),
            "trait_convergence": {},
            "most_evolved_agent": None,
            "most_stable_agent": None
        }
        
        # Trait convergence
        for trait in ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]:
            analysis["trait_convergence"][trait] = round(
                self.get_trait_convergence(trait), 3
            )
        
        # Most evolved agent (highest total drift)
        if self.agents:
            most_evolved = max(
                self.agents,
                key=lambda a: sum(
                    ev.total_drift for ev in a.trait_evolution.values()
                )
            )
            analysis["most_evolved_agent"] = {
                "name": most_evolved.agent.name,
                "total_drift": round(sum(
                    ev.total_drift for ev in most_evolved.trait_evolution.values()
                ), 3)
            }
            
            # Most stable agent (lowest total drift)
            most_stable = min(
                self.agents,
                key=lambda a: sum(
                    ev.total_drift for ev in a.trait_evolution.values()
                )
            )
            analysis["most_stable_agent"] = {
                "name": most_stable.agent.name,
                "total_drift": round(sum(
                    ev.total_drift for ev in most_stable.trait_evolution.values()
                ), 3)
            }
        
        return analysis


def create_temporal_agent(
    base_agent: Any,
    drift_rate: float = 0.01
) -> TemporalAgent:
    """
    Add temporal dynamics to an existing agent.
    
    Example:
        citizen = create_early_adopter()
        temporal = create_temporal_agent(citizen, drift_rate=0.02)
        
        # Agent evolves over time
        temporal.add_experience("Product launch success", ExperienceType.POSITIVE)
    """
    return TemporalAgent(base_agent, drift_rate)
