# examples/01_synthetic_citizens_demo.py
"""
Synthetic Citizens Demo: Beyond Static Personas

This example demonstrates how Synthetic Citizens provide behavioral
simulation that goes beyond traditional user personas.

Accompanying Article: "The Rise of Synthetic Citizens"
"""

import sys
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich import box

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from simulacrum.agents.persona import (
    Citizen, 
    PsychologicalProfile,
    create_early_adopter,
    create_skeptic,
    create_anxious_user
)

console = Console()

def print_header():
    """Display welcome header"""
    console.print(Panel.fit(
        "[bold cyan]Simulacrum: Synthetic Citizens Demo[/bold cyan]\n"
        "[dim]Behavioral Simulation Beyond Static Personas[/dim]",
        border_style="cyan",
        box=box.DOUBLE
    ))

def display_citizen_profile(citizen: Citizen):
    """Display detailed citizen profile"""
    profile_text = f"[bold]{citizen.name}[/bold] - {citizen.role}\n\n"
    profile_text += citizen.get_personality_summary()
    
    if citizen.backstory:
        profile_text += f"\n\n[dim]Background:[/dim]\n{citizen.backstory}"
    
    if citizen.core_values:
        profile_text += f"\n\n[dim]Core Values:[/dim] {', '.join(citizen.core_values)}"
    
    return Panel(profile_text, border_style="blue", title=f"👤 {citizen.name}", box=box.ROUNDED)

def run_product_test():
    """Scenario 1: Testing a financial product announcement"""
    console.print("\n[bold yellow]═══ SCENARIO 1: Product Launch Testing ═══[/bold yellow]\n")
    
    # The stimulus - a marketing message
    marketing_message = (
        "Introducing 'Auto-Invest Plus' - Our AI analyzes market trends 24/7 "
        "and automatically rebalances your portfolio while you sleep. "
        "Early adopters get 3 months free!"
    )
    
    console.print(Panel(marketing_message, title="[bold]Marketing Message[/bold]", border_style="yellow"))
    
    # Create diverse citizens
    citizens = [
        create_early_adopter(name="Alex"),
        create_skeptic(name="Barbara"),
        create_anxious_user(name="Charlie")
    ]
    
    # Display citizen profiles
    console.print("\n[bold]Test Participants:[/bold]\n")
    columns = Columns([display_citizen_profile(c) for c in citizens], equal=True, expand=True)
    console.print(columns)
    
    # Collect reactions
    console.print("\n[bold]Collecting Reactions...[/bold]\n")
    
    results_table = Table(title="Behavioral Simulation Results", box=box.ROUNDED)
    results_table.add_column("Citizen", style="cyan", no_wrap=True)
    results_table.add_column("Key Traits", style="magenta")
    results_table.add_column("Reaction", style="green", max_width=50)
    
    with console.status("[bold green]Simulating reactions...[/bold green]"):
        for citizen in citizens:
            reaction = citizen.think(
                stimulus=marketing_message,
                context="This is a new financial product being marketed to you"
            )
            
            # Extract key traits for display
            key_traits = f"Open: {citizen.traits.openness:.1f}\n"
            key_traits += f"Neuro: {citizen.traits.neuroticism:.1f}\n"
            key_traits += f"Consc: {citizen.traits.conscientiousness:.1f}"
            
            results_table.add_row(citizen.name, key_traits, reaction)
    
    console.print(results_table)
    
    return citizens

def run_crisis_communication_test(citizens: list):
    """Scenario 2: Testing crisis communication"""
    console.print("\n\n[bold yellow]═══ SCENARIO 2: Crisis Communication Testing ═══[/bold yellow]\n")
    
    crisis_message = (
        "URGENT: Due to technical issues, Auto-Invest services will be temporarily "
        "unavailable for 24-48 hours. Your funds are safe, but no trades will execute "
        "during this period."
    )
    
    console.print(Panel(crisis_message, title="[bold red]Emergency Communication[/bold red]", border_style="red"))
    
    console.print("\n[bold]Testing same message with same participants:[/bold]\n")
    
    crisis_table = Table(title="Crisis Response Patterns", box=box.ROUNDED)
    crisis_table.add_column("Citizen", style="cyan")
    crisis_table.add_column("Initial Reaction", style="yellow", max_width=40)
    crisis_table.add_column("Follow-up Question", style="red", max_width=40)
    
    with console.status("[bold green]Simulating crisis responses...[/bold green]"):
        for citizen in citizens:
            # Initial reaction
            initial = citizen.think(
                stimulus=crisis_message,
                context="You just received this notification about your investment service"
            )
            
            # Follow-up to test memory/consistency
            followup_prompt = "What are you going to do next?"
            followup = citizen.think(followup_prompt)
            
            crisis_table.add_row(citizen.name, initial, followup)
    
    console.print(crisis_table)

def run_comparative_analysis(citizens: list):
    """Scenario 3: Show behavioral consistency across contexts"""
    console.print("\n\n[bold yellow]═══ SCENARIO 3: Behavioral Consistency Analysis ═══[/bold yellow]\n")
    
    test_scenarios = [
        ("New Feature", "We're adding social sharing to your investment dashboard!"),
        ("Price Change", "Starting next month, fees increase from $9.99 to $14.99/month."),
        ("Privacy Update", "We're now sharing anonymized trading data with research partners.")
    ]
    
    consistency_table = Table(title="Cross-Context Behavioral Patterns", box=box.HEAVY_EDGE)
    consistency_table.add_column("Scenario", style="cyan")
    
    for citizen in citizens:
        consistency_table.add_column(f"{citizen.name}\n({citizen.role})", style="magenta", max_width=30)
    
    for scenario_name, scenario_text in test_scenarios:
        row_data = [scenario_name]
        
        with console.status(f"[bold green]Testing: {scenario_name}...[/bold green]"):
            for citizen in citizens:
                reaction = citizen.think(scenario_text, context="Product update notification")
                # Truncate for table display
                row_data.append(reaction[:100] + "..." if len(reaction) > 100 else reaction)
        
        consistency_table.add_row(*row_data)
    
    console.print(consistency_table)

def display_insights():
    """Display key insights from the simulation"""
    console.print("\n\n[bold yellow]═══ KEY INSIGHTS ═══[/bold yellow]\n")
    
    insights = [
        "[bold green]✓[/bold green] Same stimulus → Different reactions (psychological diversity)",
        "[bold green]✓[/bold green] Behavioral consistency within each agent across scenarios",
        "[bold green]✓[/bold green] Reactions align with personality traits (e.g., high neuroticism = anxiety)",
        "[bold green]✓[/bold green] Memory allows for contextual, evolving responses",
        "[bold yellow]→[/bold yellow] This is not possible with static personas",
    ]
    
    for insight in insights:
        console.print(f"  {insight}")
    
    console.print("\n[dim]Traditional personas would give you demographics.\n"
                 "Synthetic Citizens give you behavioral predictions.[/dim]\n")

def main():
    print_header()
    
    # Run scenarios
    citizens = run_product_test()
    run_crisis_communication_test(citizens)
    run_comparative_analysis(citizens)
    
    # Show insights
    display_insights()
    
    # Memory summary
    console.print("\n[bold]Memory System Demonstration:[/bold]")
    for citizen in citizens:
        console.print(f"\n[cyan]{citizen.name}:[/cyan] {citizen.get_memory_summary()}")

if __name__ == "__main__":
    main()