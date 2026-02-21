# examples/02_distributed_protocols_demo.py
"""
Distributed Agentic Protocols Demo

This example demonstrates how individual Synthetic Citizens collaborate
through structured protocols to reach collective decisions.

Accompanying Article: "The Elegance of the Swarm - Distributed Agentic Protocols"
"""

import sys
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.columns import Columns

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from simulacrum.agents.persona import (
    Citizen,
    PsychologicalProfile,
    create_early_adopter,
    create_skeptic,
    create_anxious_user
)
from simulacrum.protocols.voting import VotingProtocol, quick_vote, ConsensusType
from simulacrum.protocols.jury import JuryProtocol, simulate_trial

console = Console()

def print_header():
    """Display welcome header"""
    console.print(Panel.fit(
        "[bold cyan]Simulacrum: Distributed Protocols Demo[/bold cyan]\n"
        "[dim]From Individual Minds to Collective Intelligence[/dim]",
        border_style="cyan",
        box=box.DOUBLE
    ))

def create_diverse_panel(n: int = 7) -> list:
    """Create a diverse panel of citizens for voting."""
    console.print(f"\n[bold yellow]Creating diverse panel of {n} citizens...[/bold yellow]")
    
    profiles = [
        # Early adopters (2)
        PsychologicalProfile(openness=0.9, conscientiousness=0.4, neuroticism=0.2, extraversion=0.7, agreeableness=0.6),
        PsychologicalProfile(openness=0.85, conscientiousness=0.5, neuroticism=0.15, extraversion=0.8, agreeableness=0.5),
        
        # Skeptics (2)
        PsychologicalProfile(openness=0.2, conscientiousness=0.9, neuroticism=0.4, extraversion=0.3, agreeableness=0.4),
        PsychologicalProfile(openness=0.25, conscientiousness=0.85, neuroticism=0.5, extraversion=0.4, agreeableness=0.3),
        
        # Anxious users (1)
        PsychologicalProfile(openness=0.4, conscientiousness=0.6, neuroticism=0.9, extraversion=0.3, agreeableness=0.7),
        
        # Balanced (2)
        PsychologicalProfile(openness=0.5, conscientiousness=0.5, neuroticism=0.5, extraversion=0.5, agreeableness=0.5),
        PsychologicalProfile(openness=0.55, conscientiousness=0.6, neuroticism=0.4, extraversion=0.6, agreeableness=0.6),
    ]
    
    roles = ["Tech Lead", "Product Manager", "Risk Analyst", "Compliance Officer", 
             "Customer Support", "Engineer", "Designer"]
    names = ["Alex", "Jordan", "Barbara", "Diana", "Charlie", "Sam", "Taylor"]
    
    citizens = []
    for i in range(min(n, len(profiles))):
        citizen = Citizen(
            name=names[i],
            role=roles[i],
            traits=profiles[i]
        )
        citizens.append(citizen)
    
    return citizens

def scenario_1_product_decision():
    """Scenario 1: Product team voting on a feature decision"""
    console.print("\n[bold yellow]═══ SCENARIO 1: Product Feature Decision ═══[/bold yellow]\n")
    
    console.print("A product team must decide on their next major feature.\n")
    
    # Create team
    team = create_diverse_panel(n=7)
    
    # Show team composition
    team_table = Table(title="Product Team", box=box.SIMPLE)
    team_table.add_column("Name", style="cyan")
    team_table.add_column("Role", style="magenta")
    team_table.add_column("Personality", style="yellow")
    
    for citizen in team:
        personality = f"O:{citizen.traits.openness:.1f} C:{citizen.traits.conscientiousness:.1f} N:{citizen.traits.neuroticism:.1f}"
        team_table.add_row(citizen.name, citizen.role, personality)
    
    console.print(team_table)
    
    # The decision
    question = "Which feature should we build next quarter?"
    options = [
        "AI-powered recommendation engine",
        "Advanced analytics dashboard",
        "Mobile app redesign"
    ]
    
    console.print(f"\n[bold]Question:[/bold] {question}")
    console.print("[bold]Options:[/bold]")
    for i, opt in enumerate(options, 1):
        console.print(f"  {i}. {opt}")
    
    # Run vote with simple majority
    console.print("\n[bold green]Running vote (Simple Majority)...[/bold green]")
    with console.status("[bold green]Agents deliberating...[/bold green]"):
        result = quick_vote(team, question, options, ConsensusType.SIMPLE_MAJORITY)
    
    # Display results
    results_table = Table(title="Voting Results", box=box.ROUNDED)
    results_table.add_column("Option", style="cyan")
    results_table.add_column("Votes", style="magenta")
    results_table.add_column("Supporters", style="yellow", max_width=30)
    
    for option in options:
        votes = result.vote_counts.get(option, 0)
        supporters = ", ".join(result.breakdown.get(option, []))
        results_table.add_row(option, str(votes), supporters)
    
    console.print("\n")
    console.print(results_table)
    
    console.print(f"\n[bold green]✓ Winner:[/bold green] {result.winner}")
    console.print(f"[bold]Consensus:[/bold] {result.confidence*100:.0f}% support")
    console.print(f"[bold]Decisive:[/bold] {'Yes' if result.is_decisive else 'No (tie or insufficient majority)'}")
    
    return team

def scenario_2_consensus_types(team):
    """Scenario 2: Same question, different consensus mechanisms"""
    console.print("\n\n[bold yellow]═══ SCENARIO 2: Consensus Mechanisms Compared ═══[/bold yellow]\n")
    
    console.print("Testing different consensus mechanisms on a sensitive decision.\n")
    
    question = "Should we raise prices by 25%?"
    options = ["Yes, increase prices", "No, keep current pricing", "Compromise: 15% increase"]
    
    console.print(f"[bold]Question:[/bold] {question}\n")
    
    consensus_types = [
        ConsensusType.SIMPLE_MAJORITY,
        ConsensusType.SUPERMAJORITY,
        ConsensusType.PLURALITY
    ]
    
    comparison_table = Table(title="Consensus Mechanism Comparison", box=box.HEAVY)
    comparison_table.add_column("Mechanism", style="cyan")
    comparison_table.add_column("Winner", style="green")
    comparison_table.add_column("Confidence", style="yellow")
    comparison_table.add_column("Decisive?", style="magenta")
    
    for consensus_type in consensus_types:
        with console.status(f"[bold green]Testing {consensus_type.value}...[/bold green]"):
            result = quick_vote(team, question, options, consensus_type)
        
        comparison_table.add_row(
            consensus_type.value.replace("_", " ").title(),
            result.winner[:30] + "..." if len(result.winner) > 30 else result.winner,
            f"{result.confidence*100:.0f}%",
            "✓" if result.is_decisive else "✗"
        )
    
    console.print(comparison_table)
    
    console.print("\n[bold]Insight:[/bold] Different consensus mechanisms can lead to different outcomes!")
    console.print("[dim]Supermajority is harder to achieve but provides stronger mandate.[/dim]")

def scenario_3_jury_deliberation():
    """Scenario 3: Jury deliberation with multi-round discussion"""
    console.print("\n\n[bold yellow]═══ SCENARIO 3: Jury Deliberation ═══[/bold yellow]\n")
    
    console.print("12 citizens must reach a verdict in a criminal trial.\n")
    
    # Create jury
    jury = create_diverse_panel(n=12)
    
    # Extend to 12 if needed
    while len(jury) < 12:
        jury.append(Citizen(
            name=f"Juror{len(jury)+1}",
            role="Juror",
            traits=PsychologicalProfile(
                openness=0.5,
                conscientiousness=0.6,
                neuroticism=0.4,
                extraversion=0.5,
                agreeableness=0.6
            )
        ))
    
    console.print(f"[bold]Jury enrolled:[/bold] {len(jury)} citizens\n")
    
    # The case
    case_summary = """
The defendant is accused of stealing a car from a parking lot. 
Security footage shows someone matching the defendant's description near the vehicle.
The defendant claims they were visiting a friend in the area and never touched the car.
No fingerprints were found on the vehicle. The car was found abandoned 2 miles away.
"""
    
    charges = "Grand Theft Auto"
    evidence = [
        "Security footage (grainy, shows person similar to defendant)",
        "Defendant has prior theft conviction from 10 years ago",
        "No physical evidence linking defendant to vehicle",
        "Defendant's alibi (friend) confirmed being together that evening"
    ]
    
    console.print(Panel(
        f"[bold]CHARGES:[/bold] {charges}\n\n"
        f"[bold]CASE:[/bold]{case_summary}\n"
        f"[bold]EVIDENCE:[/bold]\n" + "\n".join([f"• {e}" for e in evidence]),
        title="Case Details",
        border_style="red"
    ))
    
    # Run jury deliberation
    console.print("\n[bold green]Beginning jury deliberation...[/bold green]\n")
    
    with console.status("[bold green]Jury deliberating through multiple rounds...[/bold green]"):
        verdict = simulate_trial(
            agents=jury,
            case_summary=case_summary,
            charges=charges,
            evidence=evidence,
            max_rounds=3
        )
    
    # Display verdict
    verdict_color = "green" if verdict.consensus_reached else "yellow"
    
    console.print(f"\n[bold {verdict_color}]VERDICT: {verdict.verdict}[/bold {verdict_color}]")
    console.print(f"[bold]Rounds of deliberation:[/bold] {verdict.rounds_taken}")
    console.print(f"[bold]Consensus reached:[/bold] {'Yes' if verdict.consensus_reached else 'No (Hung Jury)'}")
    
    # Show vote trajectory
    trajectory_table = Table(title="Vote Trajectory", box=box.SIMPLE)
    trajectory_table.add_column("Round", style="cyan")
    trajectory_table.add_column("Guilty", style="red")
    trajectory_table.add_column("Not Guilty", style="green")
    
    for i, votes in enumerate(verdict.vote_trajectory):
        round_label = "Initial" if i == 0 else f"After Round {i}"
        trajectory_table.add_row(
            round_label,
            str(votes.get("Guilty", 0)),
            str(votes.get("Not Guilty", 0))
        )
    
    console.print("\n")
    console.print(trajectory_table)
    
    if verdict.consensus_reached:
        console.print(f"\n[bold green]✓ The jury reached a unanimous decision of '{verdict.verdict}'[/bold green]")
    else:
        console.print(f"\n[bold yellow]! The jury was unable to reach consensus (hung jury)[/bold yellow]")

def display_key_insights():
    """Display key insights from distributed protocols"""
    console.print("\n\n[bold yellow]═══ KEY INSIGHTS ═══[/bold yellow]\n")
    
    insights = [
        "[bold green]✓[/bold green] [bold]Emergent Intelligence:[/bold] Groups can reach decisions no single agent could",
        "[bold green]✓[/bold green] [bold]Psychological Diversity:[/bold] Different personalities lead to richer deliberation",
        "[bold green]✓[/bold green] [bold]Consensus Mechanisms Matter:[/bold] The protocol shapes the outcome",
        "[bold green]✓[/bold green] [bold]Multi-Round Discussion:[/bold] Opinions can shift based on persuasive arguments",
        "[bold yellow]→[/bold yellow] [bold]Real-World Applications:[/bold] Policy testing, jury prediction, committee simulation"
    ]
    
    for insight in insights:
        console.print(f"  {insight}")
    
    console.print("\n[dim]Traditional personas are isolated.\n"
                 "Distributed protocols enable collective intelligence.[/dim]\n")

def main():
    print_header()
    
    # Run scenarios
    team = scenario_1_product_decision()
    scenario_2_consensus_types(team)
    scenario_3_jury_deliberation()
    
    # Show insights
    display_key_insights()
    
    console.print("\n[bold cyan]Next: Article 3 - Agent-to-Agent Economies[/bold cyan]")
    console.print("[dim]Where agents don't just collaborate—they transact.[/dim]\n")

if __name__ == "__main__":
    main()