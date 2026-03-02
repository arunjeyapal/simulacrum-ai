# Article 4 Technical Guide: Algorithmic Evolution

**Complete reference for temporal dynamics, trait drift, and adaptive learning**

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Concepts](#core-concepts)
4. [API Reference](#api-reference)
5. [Common Patterns](#common-patterns)
6. [Integration Guide](#integration-guide)
7. [Troubleshooting](#troubleshooting)
8. [Performance](#performance)
9. [Advanced Topics](#advanced-topics)

---

## Overview

The Evolution Layer (Article 4) adds temporal dynamics to agents:
- **Trait Drift**: Personality changes based on experiences
- **Adaptive Learning**: Strategies improve from outcomes
- **Social Influence**: Traits converge through interaction
- **Population Learning**: Knowledge spreads culturally

**Key Innovation**: Agents aren't static—they evolve, learn, and influence each other over time.

---

## Architecture

### Layer Stack
```
┌─────────────────────────────────────┐
│   Population Learning                │  ← Cultural transmission
│  (Knowledge sharing, memes)          │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Long-Term Simulation               │  ← Time progression
│  (Interactions, market experiences)  │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Adaptive Learner                   │  ← Strategy learning
│  (Decisions, outcomes, strategies)   │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Temporal Agent                     │  ← Trait evolution
│  (Experiences, drift, memory decay)  │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Citizen (Article 1)                │  ← Base personality
└─────────────────────────────────────┘
```

### File Structure
```
src/simulacrum/evolution/
├── __init__.py          # Package exports
├── temporal.py          # Trait drift & time
└── learning.py          # Adaptive learning
```

---

## Core Concepts

### 1. Temporal Agent

An agent whose traits evolve over time:

```python
from simulacrum.evolution import create_temporal_agent

# Start with base agent
base = create_early_adopter("Alice")

# Add temporal dynamics
temporal = create_temporal_agent(
    base_agent=base,
    drift_rate=0.02  # How fast traits change
)

# Initial state
print(temporal.agent.traits.openness)  # 0.90

# Add experience
temporal.add_experience(
    description="Launch succeeded!",
    experience_type=ExperienceType.POSITIVE,
    intensity=0.8,
    trait_impacts={"openness": 0.03}
)

# Traits evolved
print(temporal.agent.traits.openness)  # 0.93
```

**Key Properties:**
- `drift_rate`: Controls evolution speed (0.0-1.0)
- `experiences`: List of all experiences
- `trait_evolution`: Tracks changes per trait
- `agent`: The underlying citizen

### 2. Experience-Driven Drift

**How experiences change personality:**

```python
from simulacrum.evolution import ExperienceType

# Positive experience → confidence
temporal.add_experience(
    "Successful product launch",
    ExperienceType.POSITIVE,
    intensity=0.9,
    trait_impacts={
        "openness": 0.02,      # More willing to innovate
        "neuroticism": -0.01   # Less anxious
    }
)

# Negative experience → caution
temporal.add_experience(
    "Product failed in market",
    ExperienceType.NEGATIVE,
    intensity=0.8,
    trait_impacts={
        "openness": -0.02,     # Less willing to risk
        "neuroticism": 0.02    # More anxious
    }
)

# Neutral experience → practice
temporal.add_experience(
    "Routine task completed",
    ExperienceType.NEUTRAL,
    intensity=0.3,
    trait_impacts={
        "conscientiousness": 0.01  # Building habit
    }
)
```

**Experience Formula:**
```
trait_change = impact * intensity * drift_rate

Example:
  impact = 0.02
  intensity = 0.8
  drift_rate = 0.02
  → change = 0.02 * 0.8 * 0.02 = 0.00032
```

### 3. Adaptive Learning

**Agents learn what works:**

```python
from simulacrum.evolution import create_adaptive_learner, OutcomeType

# Create learner
learner = create_adaptive_learner(
    base_agent=agent,
    learning_rate=0.15  # How fast they adapt
)

# Make a decision
decision = learner.record_decision(
    context="pricing",
    choice="moderate_price",
    reasoning="Balanced approach",
    confidence=0.7
)

# Outcome happens
learner.record_outcome(
    decision_id=decision.id,
    outcome_type=OutcomeType.SUCCESS,
    reward=100.0
)

# Strategy learned
best = learner.get_best_strategy("pricing")
print(best.description)      # "moderate_price"
print(best.success_rate)     # 1.0 (100% so far)
print(best.total_reward)     # 100.0
```

**Learning Mechanisms:**
1. **Reinforcement**: Success → higher success_rate
2. **Exploration**: Try new strategies when uncertain
3. **Exploitation**: Use proven strategies
4. **Vicarious**: Learn from observing others

### 4. Social Influence

**Traits converge through interaction:**

```python
# Two agents interact
agent1 = create_temporal_agent(base1, drift_rate=0.02)
agent2 = create_temporal_agent(base2, drift_rate=0.02)

# Agent1's openness: 0.50
# Agent2's openness: 0.80

# Interaction
sim = LongTermSimulation([agent1, agent2])
sim.simulate_interaction(agent1, agent2, trait_name="openness")

# After interaction:
# Agent1's openness: 0.53 (moved toward agent2)
# Agent2's openness: 0.79 (slight move toward agent1)
```

**Influence Formula:**
```
susceptibility = agent1.agreeableness * 0.1
influence_strength = agent2.extraversion
trait_diff = agent2.trait - agent1.trait

delta = trait_diff * susceptibility * influence_strength

agent1.trait += delta
```

**Key Insight**: Agreeable agents are more influenced. Extraverted agents are more influential.

### 5. Population Learning

**Knowledge spreads like memes:**

```python
from simulacrum.evolution.learning import PopulationLearning

# Population of learners
population = [
    create_adaptive_learner(agent)
    for agent in agents
]

pop_learning = PopulationLearning(population)

# Agent A discovers good strategy
population[0].record_decision("sales", "consultative_approach", "")
population[0].record_outcome(decision_id, OutcomeType.SUCCESS, 500)

# Share knowledge
pop_learning.share_knowledge()

# Other agents adopt successful strategy
for learner in population[1:]:
    strategies = learner.strategies.get("sales", [])
    # Now includes "consultative_approach" learned from Agent A
```

---

## API Reference

### TemporalAgent

```python
class TemporalAgent:
    def __init__(
        self,
        base_agent: Citizen,
        drift_rate: float = 0.02
    )
    
    def add_experience(
        self,
        description: str,
        experience_type: ExperienceType,
        intensity: float = 0.5,
        trait_impacts: Dict[str, float] = {}
    ) -> Experience:
        """
        Add experience that affects traits.
        
        Args:
            description: What happened
            experience_type: POSITIVE, NEGATIVE, or NEUTRAL
            intensity: 0.0-1.0, how strong the experience
            trait_impacts: Dict of trait_name -> change amount
        
        Returns:
            Experience object
        """
    
    def get_trait_drift(self, trait_name: str) -> float:
        """Total drift for a trait since creation"""
    
    def decay_memories(self, decay_rate: float = 0.1):
        """Simulate forgetting over time"""
    
    @property
    def experiences(self) -> List[Experience]:
        """All experiences"""
    
    @property
    def trait_evolution(self) -> Dict[str, TraitEvolution]:
        """Evolution tracking per trait"""
```

### AdaptiveLearner

```python
class AdaptiveLearner:
    def __init__(
        self,
        base_agent: Citizen,
        learning_rate: float = 0.1,
        exploration_rate: float = 0.3
    )
    
    def record_decision(
        self,
        context: str,
        choice: str,
        reasoning: str = "",
        confidence: float = 0.5
    ) -> Decision:
        """
        Record a decision made.
        
        Args:
            context: Decision category (e.g., "pricing", "hiring")
            choice: What was chosen
            reasoning: Why
            confidence: 0.0-1.0
        """
    
    def record_outcome(
        self,
        decision_id: str,
        outcome_type: OutcomeType,
        reward: float = 0.0
    ):
        """
        Record outcome of a decision.
        
        Updates strategy success rates.
        """
    
    def get_best_strategy(
        self,
        context: str
    ) -> Optional[Strategy]:
        """
        Get highest success rate strategy for context.
        
        Returns None if no strategies for context.
        """
    
    def should_explore(self) -> bool:
        """
        Decide whether to try new strategy vs use best known.
        
        Based on:
        - exploration_rate
        - openness trait
        - recent performance
        """
    
    def learn_from_observation(
        self,
        other: "AdaptiveLearner",
        context: str
    ):
        """
        Adopt strategies from observing another agent.
        Vicarious learning.
        """
```

### LongTermSimulation

```python
class LongTermSimulation:
    def __init__(self, agents: List[TemporalAgent])
    
    def advance_time(self, days: int = 1):
        """Progress simulation by days"""
    
    def simulate_interaction(
        self,
        agent1: TemporalAgent,
        agent2: TemporalAgent,
        trait_name: str
    ):
        """
        Two agents interact, traits may converge.
        """
    
    def simulate_market_experience(
        self,
        agent: TemporalAgent,
        outcome: str,
        profit: float
    ):
        """
        Agent has market experience, traits adjust.
        """
    
    def get_trait_convergence(
        self,
        trait_name: str
    ) -> float:
        """
        Measure population variance for trait.
        Lower = more convergence.
        """
    
    def analyze_evolution(self) -> Dict[str, Any]:
        """
        Statistics on population evolution:
        - Most evolved agents
        - Most stable agents
        - Trait variance over time
        """
```

### Factory Functions

```python
def create_temporal_agent(
    base_agent: Citizen,
    drift_rate: float = 0.02
) -> TemporalAgent:
    """Create agent with temporal dynamics"""

def create_adaptive_learner(
    base_agent: Citizen,
    learning_rate: float = 0.1
) -> AdaptiveLearner:
    """Create agent with learning capability"""
```

---

## Common Patterns

### Pattern 1: Simple Trait Evolution

```python
from simulacrum.evolution import create_temporal_agent, ExperienceType

# Create temporal agent
agent = create_temporal_agent(base, drift_rate=0.02)

# Track initial state
initial_openness = agent.agent.traits.openness

# Agent experiences success
for i in range(5):
    agent.add_experience(
        f"Success #{i+1}",
        ExperienceType.POSITIVE,
        intensity=0.7,
        trait_impacts={"openness": 0.02}
    )

# Check evolution
final_openness = agent.agent.traits.openness
total_drift = agent.get_trait_drift("openness")

print(f"Openness: {initial_openness:.3f} → {final_openness:.3f}")
print(f"Total drift: {total_drift:.3f}")
```

### Pattern 2: Learning from Trial and Error

```python
from simulacrum.evolution import create_adaptive_learner, OutcomeType

learner = create_adaptive_learner(agent, learning_rate=0.15)

# Try different strategies
strategies = ["aggressive", "moderate", "conservative"]

for round in range(10):
    # Explore: try random strategy
    if learner.should_explore():
        choice = random.choice(strategies)
    else:
        # Exploit: use best known
        best = learner.get_best_strategy("pricing")
        choice = best.description if best else random.choice(strategies)
    
    # Record decision
    decision = learner.record_decision(
        context="pricing",
        choice=choice
    )
    
    # Simulate outcome
    success_prob = {
        "aggressive": 0.3,
        "moderate": 0.7,
        "conservative": 0.5
    }[choice]
    
    if random.random() < success_prob:
        learner.record_outcome(decision.id, OutcomeType.SUCCESS, 100)
    else:
        learner.record_outcome(decision.id, OutcomeType.FAILURE, -20)

# Check learned strategy
best = learner.get_best_strategy("pricing")
print(f"Best strategy: {best.description}")
print(f"Success rate: {best.success_rate:.1%}")
```

### Pattern 3: Social Influence & Convergence

```python
from simulacrum.evolution import LongTermSimulation
import statistics

# Create diverse population
agents = [
    create_temporal_agent(create_early_adopter(f"Agent_{i}"), 0.02)
    for i in range(10)
]

# Randomize one trait
for agent in agents:
    agent.agent.traits.openness = random.uniform(0.3, 0.9)

# Measure initial diversity
initial_values = [a.agent.traits.openness for a in agents]
initial_std = statistics.stdev(initial_values)

# Run simulation with interactions
sim = LongTermSimulation(agents)

for day in range(30):
    # Random pairwise interactions
    agent1 = random.choice(agents)
    agent2 = random.choice(agents)
    if agent1 != agent2:
        sim.simulate_interaction(agent1, agent2, "openness")

# Measure final diversity
final_values = [a.agent.traits.openness for a in agents]
final_std = statistics.stdev(final_values)

print(f"Diversity: {initial_std:.3f} → {final_std:.3f}")
print(f"Convergence: {(initial_std - final_std) / initial_std:.1%}")
```

### Pattern 4: Population Knowledge Sharing

```python
from simulacrum.evolution.learning import PopulationLearning

# Create learner population
learners = [
    create_adaptive_learner(agent)
    for agent in agents
]

# Agent 0 discovers good strategy early
learners[0].record_decision("sales", "consultative", "")
learners[0].record_outcome("dec_1", OutcomeType.SUCCESS, 500)
learners[0].record_outcome("dec_2", OutcomeType.SUCCESS, 600)

# Population learning
pop = PopulationLearning(learners)

# Share knowledge
for generation in range(5):
    pop.share_knowledge()
    
    # Check adoption
    stats = pop.get_population_statistics()
    print(f"Gen {generation}:")
    print(f"  Unique strategies: {stats['unique_strategies']}")
    print(f"  Avg strategies/agent: {stats['avg_strategies_per_agent']:.1f}")
```

### Pattern 5: Combined Evolution & Learning

```python
# Agent with both capabilities
base = create_early_adopter("Alice")
temporal = create_temporal_agent(base, drift_rate=0.02)
learner = create_adaptive_learner(temporal.agent, learning_rate=0.15)

# Decision → Outcome → Learning → Trait Evolution
for trial in range(20):
    # Make decision with current traits
    decision = learner.record_decision("strategy", "innovative")
    
    # Outcome
    success = random.random() < 0.6
    
    if success:
        # Learn strategy works
        learner.record_outcome(decision.id, OutcomeType.SUCCESS, 100)
        
        # Traits evolve (success → confidence)
        temporal.add_experience(
            "Strategy succeeded",
            ExperienceType.POSITIVE,
            trait_impacts={"openness": 0.01, "neuroticism": -0.01}
        )
    else:
        # Learn strategy failed
        learner.record_outcome(decision.id, OutcomeType.FAILURE, -20)
        
        # Traits evolve (failure → caution)
        temporal.add_experience(
            "Strategy failed",
            ExperienceType.NEGATIVE,
            trait_impacts={"openness": -0.01, "neuroticism": 0.01}
        )

# Agent both learned AND evolved
print(f"Best strategy: {learner.get_best_strategy('strategy').description}")
print(f"Openness changed: {temporal.get_trait_drift('openness'):.3f}")
```

---

## Integration Guide

### With Article 1 (Personas)

```python
from simulacrum.agents import create_early_adopter
from simulacrum.evolution import create_temporal_agent

# Start with persona
base = create_early_adopter("Alice")

# Add evolution
temporal = create_temporal_agent(base, drift_rate=0.02)

# Personality now evolves
# Still consistent with early adopter archetype
# But adapts based on experiences
```

### With Article 3 (Economy)

```python
from simulacrum.economy import create_economic_citizen
from simulacrum.evolution import create_temporal_agent

# Economic + temporal
base = create_economic_citizen("Alice", "Trader", traits, 10000)
temporal = create_temporal_agent(base, drift_rate=0.02)

# Economic experiences affect traits
for trade in range(100):
    profit = execute_trade(temporal.agent)
    
    if profit > 0:
        temporal.add_experience(
            "Profitable trade",
            ExperienceType.POSITIVE,
            trait_impacts={"openness": 0.01}  # Success → risk-seeking
        )
    else:
        temporal.add_experience(
            "Loss",
            ExperienceType.NEGATIVE,
            trait_impacts={"neuroticism": 0.01}  # Loss → anxious
        )

# Traits evolve based on economic performance
```

### With Article 5 (Governance)

```python
from simulacrum.governance import Guardrails, TraitBoundary
from simulacrum.evolution import create_temporal_agent

# Temporal + governance
temporal = create_temporal_agent(base, drift_rate=0.02)

# Governance prevents dangerous drift
policy = GovernancePolicy(
    trait_boundaries=[
        TraitBoundary("openness", max_value=0.95)
    ]
)

guardrails = Guardrails(policy)

# Agent evolves but within bounds
temporal.add_experience("Big success", ExperienceType.POSITIVE,
                       trait_impacts={"openness": 0.10})

# Check governance
violations = guardrails.check_trait_boundaries(temporal.agent)
# If openness > 0.95, auto-corrected to 0.95
```

---

## Troubleshooting

### Problem: Traits Drift Too Fast

**Symptom**: Agents change dramatically in a few experiences

**Cause**: `drift_rate` too high

**Solution**:
```python
# TOO HIGH - unrealistic
temporal = create_temporal_agent(base, drift_rate=0.5)  # 50% adaptation

# REALISTIC
temporal = create_temporal_agent(base, drift_rate=0.02)  # 2% adaptation

# Traits change gradually over many experiences
```

### Problem: No Learning Happening

**Symptom**: Agent keeps trying same failed strategy

**Cause**: Not recording outcomes

**Solution**:
```python
# BAD - decision without outcome
decision = learner.record_decision("pricing", "high_price")
# No learning!

# GOOD - record outcome
decision = learner.record_decision("pricing", "high_price")
learner.record_outcome(decision.id, OutcomeType.FAILURE, -50)
# Now agent learns high_price doesn't work
```

### Problem: Social Influence Not Working

**Symptom**: Traits don't converge despite interactions

**Cause**: Low agreeableness or extraversion

**Solution**:
```python
# Check traits
print(f"Agent 1 agreeableness: {agent1.agent.traits.agreeableness}")
print(f"Agent 2 extraversion: {agent2.agent.traits.extraversion}")

# If both low, influence is weak
# This is actually realistic! 
# Not all agents are susceptible to influence

# To force convergence (for testing):
agent1.agent.traits.agreeableness = 0.8  # More susceptible
agent2.agent.traits.extraversion = 0.8   # More influential
```

### Problem: Traits Exceed Bounds

**Symptom**: openness = 1.2 or neuroticism = -0.1

**Cause**: Not constraining to [0, 1]

**Solution**:
```python
# Built into temporal.py, but if implementing custom:
def apply_trait_change(self, trait_name, delta):
    current = getattr(self.agent.traits, trait_name)
    new_value = current + delta
    
    # CRITICAL: Constrain to valid range
    new_value = max(0.0, min(1.0, new_value))
    
    setattr(self.agent.traits, trait_name, new_value)
```

---

## Performance

### Benchmarks

**Single Operations:**
- Add experience: <1ms
- Trait adjustment: <1ms
- Record decision: <1ms
- Record outcome: <1ms

**Social Interaction:**
- simulate_interaction (with LLM memory): ~5 seconds
- simulate_interaction (without LLM): <1ms

**Population Simulation:**
- 10 agents, 30 days, 100 interactions: ~8 minutes
- 100 agents, 10 days, 500 interactions: ~45 minutes

**Bottleneck**: LLM calls for memory/reasoning

### Optimization

**1. Disable LLM for Fast Simulation**
```python
# For large-scale simulations, use pure math
sim = LongTermSimulation(agents, use_llm=False)

# 100x faster, but less realistic reasoning
```

**2. Batch Social Interactions**
```python
# Instead of sequential
for i in range(100):
    sim.simulate_interaction(a1, a2, "openness")

# Batch process
interaction_pairs = [(a1, a2) for _ in range(100)]
sim.batch_simulate_interactions(interaction_pairs, "openness")
```

**3. Parallel Population Learning**
```python
from concurrent.futures import ThreadPoolExecutor

def learn_agent(learner):
    # Each agent learns independently
    pass

with ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(learn_agent, learners)
```

---

## Advanced Topics

### Custom Experience Impact Functions

```python
class CustomTemporalAgent(TemporalAgent):
    def calculate_trait_impact(self, experience: Experience) -> Dict[str, float]:
        """Custom logic for how experiences affect traits"""
        
        impacts = {}
        
        if experience.type == ExperienceType.POSITIVE:
            # Success impacts based on intensity
            if experience.intensity > 0.8:
                impacts["openness"] = 0.03  # Big success → confident
                impacts["neuroticism"] = -0.02
            else:
                impacts["openness"] = 0.01  # Small success
        
        elif experience.type == ExperienceType.NEGATIVE:
            # Failure impacts based on current neuroticism
            if self.agent.traits.neuroticism > 0.7:
                impacts["neuroticism"] = 0.05  # Anxious get more anxious
            else:
                impacts["neuroticism"] = 0.02
        
        return impacts
```

### Contextual Learning Rates

```python
class AdaptiveRateLearner(AdaptiveLearner):
    def get_learning_rate(self, context: str) -> float:
        """Different learning rates for different contexts"""
        
        rates = {
            "high_stakes": 0.25,    # Learn quickly from important decisions
            "routine": 0.05,         # Learn slowly from routine
            "experimental": 0.15     # Moderate learning from experiments
        }
        
        return rates.get(context, self.learning_rate)
```

### Memory Decay & Recency

```python
def weighted_success_rate(strategy: Strategy) -> float:
    """Weight recent outcomes more heavily"""
    
    outcomes = strategy.outcomes
    if not outcomes:
        return 0.0
    
    total_weighted = 0.0
    total_weights = 0.0
    
    for i, outcome in enumerate(outcomes):
        # Recent outcomes have higher weight
        weight = 1.0 + (i / len(outcomes))  # Linear increase
        
        total_weighted += (1 if outcome.type == OutcomeType.SUCCESS else 0) * weight
        total_weights += weight
    
    return total_weighted / total_weights if total_weights > 0 else 0.0
```

---

## Best Practices

✅ **DO:**
- Start with low drift_rate (0.01-0.03) for realistic evolution
- Record both decisions AND outcomes for learning
- Use social influence for population convergence
- Track trait evolution history for debugging
- Constrain traits to [0, 1] range

❌ **DON'T:**
- Use drift_rate > 0.1 (unrealistically fast change)
- Forget to record outcomes (breaks learning)
- Assume instant convergence (takes many interactions)
- Let traits exceed valid ranges
- Ignore personality when calculating impacts

---

## Further Reading

- **Article 1**: Base personality traits
- **Article 3**: Economic decisions that create experiences
- **Reinforcement Learning**: Sutton & Barto
- **Social Learning Theory**: Bandura
- **Personality Development**: Costa & McCrae

---

**Next**: Article 5 Technical Guide (Governance & Safety)
