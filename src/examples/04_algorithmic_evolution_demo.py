# examples/04_algorithmic_evolution_demo.py
"""
Algorithmic Evolution Demo

This example demonstrates how Synthetic Citizens evolve over time through:
- Experience accumulation
- Trait drift
- Learning from outcomes
- Social influence

Accompanying Article: "Algorithmic Evolution: When Agents Drift"
"""

import sys
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.progress import track
import time

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from simulacrum.agents.persona import (
    PsychologicalProfile,
    create_early_adopter,
    create_skeptic,
    create_anxious_user
)
from simulacrum.evolution.temporal import (
    create_temporal_agent,
    ExperienceType,
    LongTermSimulation
)
from simulacrum.evolution.learning import (
    create_adaptive_learner,
    OutcomeType,
    PopulationLearning
)

console = Console()


def print_header():
    """Display welcome header"""
    console.print(Panel.fit(
        "[bold cyan]Simulacrum: Algorithmic Evolution Demo[/bold cyan]\n"
        "[dim]When Today's Safe AI Becomes Tomorrow's Unpredictable Actor[/dim]",
        border_style="cyan",
        box=box.DOUBLE
    ))


def create_population():
    """Create a population of agents to track over time."""
    console.print("\n[bold yellow]Creating agent population...[/bold yellow]")
    
    # Create base agents with different personalities
    agents = [
        create_early_adopter(name="Alex"),
        create_skeptic(name="Barbara"),
        create_anxious_user(name="Charlie"),
    ]
    
    # Add temporal dynamics
    temporal_agents = [
        create_temporal_agent(agent, drift_rate=0.02)
        for agent in agents
    ]
    
    # Display initial state
    initial_table = Table(title="Initial Population", box=box.SIMPLE)
    initial_table.add_column("Name", style="cyan")
    initial_table.add_column("O", style="yellow")
    initial_table.add_column("C", style="yellow")
    initial_table.add_column("E", style="yellow")
    initial_table.add_column("A", style="yellow")
    initial_table.add_column("N", style="yellow")
    
    for ta in temporal_agents:
        traits = ta.agent.traits
        initial_table.add_row(
            ta.agent.name,
            f"{traits.openness:.2f}",
            f"{traits.conscientiousness:.2f}",
            f"{traits.extraversion:.2f}",
            f"{traits.agreeableness:.2f}",
            f"{traits.neuroticism:.2f}"
        )
    
    console.print(initial_table)
    console.print("\n[dim]O=Openness C=Conscientiousness E=Extraversion A=Agreeableness N=Neuroticism[/dim]\n")
    
    return temporal_agents


def scenario_1_experience_shapes_personality(agents):
    """Scenario 1: Experiences cause personality drift"""
    console.print("\n[bold yellow]═══ SCENARIO 1: Experience-Driven Drift ═══[/bold yellow]\n")
    
    console.print("Agents undergo different experiences over 90 days.\n")
    
    alex, barbara, charlie = agents
    
    # Alex has positive experiences (success breeds confidence)
    console.print("[bold green]Alex (Early Adopter)[/bold green] - Series of successful launches")
    for i in range(5):
        alex.add_experience(
            description=f"Product launch #{i+1} exceeded targets",
            experience_type=ExperienceType.POSITIVE,
            intensity=0.8,
            context="Product management",
            trait_impacts={
                "openness": 0.03,      # More willing to try new things
                "neuroticism": -0.02   # Less anxious
            }
        )
        time.sleep(0.1)  # Brief pause for effect
    
    # Barbara has mixed experiences (careful approach vindicated)
    console.print("\n[bold yellow]Barbara (Skeptic)[/bold yellow] - Cautious approach prevents disasters")
    for i in range(5):
        barbara.add_experience(
            description=f"Careful analysis avoided mistake #{i+1}",
            experience_type=ExperienceType.POSITIVE,
            intensity=0.6,
            context="Risk management",
            trait_impacts={
                "conscientiousness": 0.02,  # Reinforces careful behavior
                "openness": -0.01           # Less open to risk
            }
        )
        time.sleep(0.1)
    
    # Charlie has negative experiences (failures increase anxiety)
    console.print("\n[bold red]Charlie (Anxious User)[/bold red] - Series of setbacks")
    for i in range(5):
        charlie.add_experience(
            description=f"Initiative #{i+1} faced unexpected problems",
            experience_type=ExperienceType.NEGATIVE,
            intensity=0.7,
            context="Project execution",
            trait_impacts={
                "neuroticism": 0.04,   # More anxious
                "openness": -0.02      # More conservative
            }
        )
        time.sleep(0.1)
    
    # Show trait changes
    console.print("\n[bold]Trait Changes After 90 Days:[/bold]\n")
    
    changes_table = Table(box=box.ROUNDED)
    changes_table.add_column("Agent", style="cyan")
    changes_table.add_column("Trait", style="magenta")
    changes_table.add_column("Initial", style="yellow")
    changes_table.add_column("Final", style="yellow")
    changes_table.add_column("Change", style="green")
    
    for agent in agents:
        summary = agent.summarize_evolution()
        for trait_name, changes in summary["trait_changes"].items():
            if abs(changes["change"]) > 0.01:  # Only show meaningful changes
                changes_table.add_row(
                    agent.agent.name,
                    trait_name.capitalize(),
                    f"{changes['initial']:.2f}",
                    f"{changes['current']:.2f}",
                    f"{changes['change']:+.2f}"
                )
    
    console.print(changes_table)
    
    console.print("\n[bold]Insight:[/bold] Personality isn't fixed—it evolves with experience!")
    console.print("[dim]- Success → More openness, less neuroticism[/dim]")
    console.print("[dim]- Careful wins → More conscientiousness[/dim]")
    console.print("[dim]- Failures → More anxiety, less openness[/dim]\n")


def scenario_2_social_influence(agents):
    """Scenario 2: Agents influence each other through interaction"""
    console.print("\n[bold yellow]═══ SCENARIO 2: Social Influence & Convergence ═══[/bold yellow]\n")
    
    console.print("Agents interact frequently. Do their personalities converge?\n")
    
    alex, barbara, charlie = agents
    
    # Create simulation
    sim = LongTermSimulation(agents)
    
    # Simulate 30 interactions over 60 days
    console.print("[bold green]Simulating 30 interactions over 60 days...[/bold green]\n")
    
    for i in track(range(30), description="Interactions"):
        # Rotate through different pairs
        if i % 3 == 0:
            sim.simulate_interaction(alex, barbara, "collaboration")
        elif i % 3 == 1:
            sim.simulate_interaction(barbara, charlie, "consultation")
        else:
            sim.simulate_interaction(alex, charlie, "brainstorming")
        
        # Advance time
        sim.advance_time(days=2)
        time.sleep(0.05)
    
    # Analyze convergence
    analysis = sim.analyze_evolution()
    
    console.print("\n[bold]Trait Convergence Analysis:[/bold]\n")
    
    convergence_table = Table(box=box.SIMPLE)
    convergence_table.add_column("Trait", style="cyan")
    convergence_table.add_column("Std Dev", style="yellow")
    convergence_table.add_column("Convergence", style="magenta")
    
    for trait, std_dev in analysis["trait_convergence"].items():
        # Lower std dev = more convergence
        convergence_level = "High" if std_dev < 0.15 else "Medium" if std_dev < 0.25 else "Low"
        convergence_table.add_row(
            trait.capitalize(),
            f"{std_dev:.3f}",
            convergence_level
        )
    
    console.print(convergence_table)
    
    console.print(f"\n[bold]Total Interactions:[/bold] {analysis['total_interactions']}")
    console.print(f"[bold]Most Evolved:[/bold] {analysis['most_evolved_agent']['name']} "
                 f"(drift: {analysis['most_evolved_agent']['total_drift']:.3f})")
    console.print(f"[bold]Most Stable:[/bold] {analysis['most_stable_agent']['name']} "
                 f"(drift: {analysis['most_stable_agent']['total_drift']:.3f})")
    
    console.print("\n[bold]Insight:[/bold] Social interaction causes trait convergence!")
    console.print("[dim]- High agreeableness → susceptible to influence[/dim]")
    console.print("[dim]- High extraversion → influences others more[/dim]")
    console.print("[dim]- Traits gradually align through repeated contact[/dim]\n")


def scenario_3_learning_from_outcomes(agents):
    """Scenario 3: Agents learn optimal strategies through trial and error"""
    console.print("\n[bold yellow]═══ SCENARIO 3: Adaptive Learning ═══[/bold yellow]\n")
    
    console.print("Agents try different strategies and learn which work best.\n")
    
    alex, barbara, charlie = agents
    
    # Add learning capability
    learners = [
        create_adaptive_learner(agent.agent, learning_rate=0.15)
        for agent in [alex, barbara, charlie]
    ]
    
    # Simulate 20 pricing decisions
    console.print("[bold green]Simulating 20 pricing decisions...[/bold green]\n")
    
    import random
    strategies = [
        ("aggressive", 0.4),   # 40% success rate
        ("moderate", 0.7),     # 70% success rate
        ("conservative", 0.5)  # 50% success rate
    ]
    
    for round_num in track(range(20), description="Decisions"):
        for learner in learners:
            # Decide: explore or exploit?
            if learner.should_explore() or round_num < 5:
                # Try random strategy
                strategy, success_prob = random.choice(strategies)
            else:
                # Use best known strategy
                best = learner.get_best_strategy("pricing")
                if best:
                    # Extract strategy from description
                    strategy = best.description.split("'")[1]
                    success_prob = best.success_rate
                else:
                    strategy, success_prob = random.choice(strategies)
            
            # Record decision
            decision = learner.record_decision(
                context="pricing",
                choice=strategy,
                reasoning=f"Round {round_num+1} pricing strategy",
                confidence=success_prob
            )
            
            # Simulate outcome
            success = random.random() < success_prob
            reward = 100 if success else -50
            
            outcome_type = OutcomeType.SUCCESS if success else OutcomeType.FAILURE
            learner.record_outcome(
                decision.id,
                outcome_type,
                reward=reward,
                feedback=f"Strategy {'worked' if success else 'failed'}"
            )
        
        time.sleep(0.05)
    
    # Show learning results
    console.print("\n[bold]Learning Outcomes:[/bold]\n")
    
    learning_table = Table(box=box.ROUNDED)
    learning_table.add_column("Agent", style="cyan")
    learning_table.add_column("Decisions", style="yellow")
    learning_table.add_column("Success Rate", style="green")
    learning_table.add_column("Best Strategy", style="magenta")
    learning_table.add_column("Strategy Success", style="yellow")
    
    for i, learner in enumerate(learners):
        perf = learner.get_performance_summary()
        best_strat = perf.get("best_strategy", {})
        
        learning_table.add_row(
            agents[i].agent.name,
            str(perf["total_decisions"]),
            f"{perf['success_rate']:.1%}",
            best_strat.get("description", "N/A").split("'")[1] if "'" in best_strat.get("description", "") else "N/A",
            f"{best_strat.get('success_rate', 0):.1%}" if best_strat else "N/A"
        )
    
    console.print(learning_table)
    
    console.print("\n[bold]Insight:[/bold] Agents discover optimal strategies through experience!")
    console.print("[dim]- High openness → explores more, finds best strategies faster[/dim]")
    console.print("[dim]- Success reinforces strategies, failure discourages them[/dim]")
    console.print("[dim]- Population converges on effective approaches[/dim]\n")


def scenario_4_population_knowledge_sharing(agents):
    """Scenario 4: Knowledge spreads through population"""
    console.print("\n[bold yellow]═══ SCENARIO 4: Cultural Knowledge Transmission ═══[/bold yellow]\n")
    
    console.print("What if agents could learn from observing each other?\n")
    
    # Create learners
    learners = [
        create_adaptive_learner(agent.agent, learning_rate=0.1)
        for agent in agents
    ]
    
    # Give one agent a head start with good strategies
    console.print("[bold green]Alex[/bold green] discovers effective strategies early...\n")
    
    # Alex learns "moderate" strategy works well
    for i in range(10):
        decision = learners[0].record_decision("pricing", "moderate")
        learners[0].record_outcome(
            decision.id,
            OutcomeType.SUCCESS,
            reward=100
        )
    
    # Create population learning system
    pop_learning = PopulationLearning(learners)
    
    # Simulate knowledge sharing over time
    console.print("[bold green]Agents interact and share knowledge...[/bold green]\n")
    
    for generation in track(range(10), description="Generations"):
        pop_learning.share_knowledge(interaction_probability=0.4)
        pop_learning.generation += 1
        time.sleep(0.1)
    
    # Analyze population
    stats = pop_learning.get_population_statistics()
    
    console.print("\n[bold]Population Knowledge:[/bold]\n")
    console.print(f"[bold]Total Strategies:[/bold] {stats['total_strategies']}")
    console.print(f"[bold]Avg Per Agent:[/bold] {stats['avg_strategies_per_agent']}")
    console.print(f"[bold]Population Success:[/bold] {stats['population_success_rate']:.1%}")
    
    if stats["shared_strategies"]:
        console.print("\n[bold]Most Common Successful Strategies:[/bold]")
        for i, strat in enumerate(stats["shared_strategies"], 1):
            console.print(f"  {i}. {strat['description']}")
            console.print(f"     Adopted by: {strat['adoption']} agents")
            console.print(f"     Success rate: {strat['avg_success']:.1%}\n")
    
    console.print("[bold]Insight:[/bold] Knowledge spreads like culture!")
    console.print("[dim]- Successful strategies transmitted through observation[/dim]")
    console.print("[dim]- Population becomes more effective over time[/dim]")
    console.print("[dim]- Emergent collective intelligence without central coordination[/dim]\n")


def display_key_insights():
    """Display key insights from algorithmic evolution"""
    console.print("\n[bold yellow]═══ KEY INSIGHTS ═══[/bold yellow]\n")
    
    insights = [
        "[bold green]✓[/bold green] [bold]Personality Drift:[/bold] Traits evolve based on experiences",
        "[bold green]✓[/bold green] [bold]Social Convergence:[/bold] Interaction causes trait alignment",
        "[bold green]✓[/bold green] [bold]Adaptive Learning:[/bold] Agents discover optimal strategies",
        "[bold green]✓[/bold green] [bold]Cultural Transmission:[/bold] Knowledge spreads through population",
        "[bold yellow]⚠[/bold yellow] [bold]Unpredictability:[/bold] Today's safe AI ≠ tomorrow's behavior",
        "[bold red]![/bold red] [bold]Safety Implications:[/bold] Evolution can lead to unintended outcomes"
    ]
    
    for insight in insights:
        console.print(f"  {insight}")
    
    console.print("\n[dim]Static agents are a fiction.\n"
                 "Real systems evolve, adapt, and sometimes surprise us.[/dim]\n")


def main():
    print_header()
    
    # Create population
    agents = create_population()
    
    # Run scenarios
    scenario_1_experience_shapes_personality(agents)
    scenario_2_social_influence(agents)
    scenario_3_learning_from_outcomes(agents)
    scenario_4_population_knowledge_sharing(agents)
    
    # Show insights
    display_key_insights()
    
    console.print("\n[bold cyan]Next: Article 5 - Governance as Architecture[/bold cyan]")
    console.print("[dim]How to design systems that remain safe as they evolve.[/dim]\n")


if __name__ == "__main__":
    main()
