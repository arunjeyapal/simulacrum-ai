# src/simulacrum/evolution/__init__.py
"""
Temporal dynamics and learning for agents.

Enables agents to:
- Evolve personality traits over time
- Learn from experience and outcomes
- Influence each other socially
- Adapt strategies based on feedback
"""

from simulacrum.evolution.temporal import (
    TemporalAgent,
    Experience,
    ExperienceType,
    TraitEvolution,
    LongTermSimulation,
    create_temporal_agent
)

from simulacrum.evolution.learning import (
    AdaptiveLearner,
    Decision,
    Outcome,
    OutcomeType,
    Strategy,
    PopulationLearning,
    create_adaptive_learner
)

__all__ = [
    # Temporal Dynamics
    "TemporalAgent",
    "Experience",
    "ExperienceType",
    "TraitEvolution",
    "LongTermSimulation",
    "create_temporal_agent",
    
    # Adaptive Learning
    "AdaptiveLearner",
    "Decision",
    "Outcome",
    "OutcomeType",
    "Strategy",
    "PopulationLearning",
    "create_adaptive_learner",
]
