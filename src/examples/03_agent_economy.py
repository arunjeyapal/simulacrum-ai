# examples/03_agent_economy_demo.py
"""
Agent-to-Agent Economy Demo

This example demonstrates how Synthetic Citizens engage in economic
transactions: buying, selling, negotiating, and forming markets.

Accompanying Article: "The Agent-to-Agent Economy"
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
    PsychologicalProfile,
)
from simulacrum.economy.wallet import (
    create_economic_citizen,
    Wallet,
    calculate_utility
)
from simulacrum.economy.negotiation import (
    negotiate_price,
    NegotiationOutcome
)
from simulacrum.economy.marketplace import (
    simulate_market,
    analyze_price_sensitivity
)

console = Console()


def print_header():
    """Display welcome header"""
    console.print(Panel.fit(
        "[bold cyan]Simulacrum: Agent-to-Agent Economy Demo[/bold cyan]\n"
        "[dim]Where Agents Don't Just Collaborate—They Transact[/dim]",
        border_style="cyan",
        box=box.DOUBLE
    ))


def create_economic_agents():
    """Create agents with economic capabilities."""
    console.print("\n[bold yellow]Creating economic agents...[/bold yellow]")
    
    agents = [
        # High openness - values innovation, willing to pay premium
        create_economic_citizen(
            name="Alex",
            role="Tech Innovator",
            traits=PsychologicalProfile(
                openness=0.9,
                conscientiousness=0.6,
                extraversion=0.7,
                agreeableness=0.6,
                neuroticism=0.3
            ),
            initial_balance=2000
        ),
        
        # High conscientiousness - careful buyer, values quality
        create_economic_citizen(
            name="Barbara",
            role="CFO",
            traits=PsychologicalProfile(
                openness=0.4,
                conscientiousness=0.9,
                extraversion=0.5,
                agreeableness=0.6,
                neuroticism=0.4
            ),
            initial_balance=3000
        ),
        
        # High neuroticism - risk averse, cautious spender
        create_economic_citizen(
            name="Charlie",
            role="Risk Analyst",
            traits=PsychologicalProfile(
                openness=0.5,
                conscientiousness=0.7,
                extraversion=0.4,
                agreeableness=0.7,
                neuroticism=0.9
            ),
            initial_balance=1500
        ),
        
        # High agreeableness - quick to agree, fair negotiator
        create_economic_citizen(
            name="Diana",
            role="Partnership Manager",
            traits=PsychologicalProfile(
                openness=0.6,
                conscientiousness=0.6,
                extraversion=0.8,
                agreeableness=0.9,
                neuroticism=0.3
            ),
            initial_balance=2500
        )
    ]
    
    # Display agents
    agent_table = Table(title="Economic Agents", box=box.SIMPLE)
    agent_table.add_column("Name", style="cyan")
    agent_table.add_column("Role", style="magenta")
    agent_table.add_column("Balance", style="green")
    agent_table.add_column("Key Trait", style="yellow")
    
    for agent in agents:
        traits = agent.traits
        key_trait = max(
            [("Open", traits.openness),
             ("Conscientious", traits.conscientiousness),
             ("Neurotic", traits.neuroticism),
             ("Agreeable", traits.agreeableness),
             ("Extraverted", traits.extraversion)],
            key=lambda x: x[1]
        )[0]
        
        agent_table.add_row(
            agent.name,
            agent.role,
            f"{agent.wallet.balance:.0f} credits",
            key_trait
        )
    
    console.print(agent_table)
    return agents


def scenario_1_utility_valuation(agents):
    """Scenario 1: How agents value the same product differently"""
    console.print("\n[bold yellow]═══ SCENARIO 1: Differential Valuation ═══[/bold yellow]\n")
    
    console.print("All agents evaluate the same product: 'AI-Powered Analytics Platform'\n")
    
    # Product context
    item = "AI-Powered Analytics Platform"
    base_value = 500
    context = {
        "base_value": base_value,
        "novelty_bonus": 200,  # It's innovative
        "quality_premium": 150,  # High quality
        "risk_adjustment": -100,  # Some implementation risk
        "reviews": 85,  # Good social proof
        "description": "Cutting-edge analytics with ML capabilities"
    }
    
    # Calculate utilities
    valuations = []
    for agent in agents:
        utility = calculate_utility(agent, item, base_value, context)
        valuations.append((agent.name, agent.role, utility))
    
    # Display results
    valuation_table = Table(title="Agent Valuations (Willingness-to-Pay)", box=box.ROUNDED)
    valuation_table.add_column("Agent", style="cyan")
    valuation_table.add_column("Role", style="magenta")
    valuation_table.add_column("Valuation", style="green")
    valuation_table.add_column("Premium vs Base", style="yellow")
    
    for name, role, utility in valuations:
        premium = utility - base_value
        premium_pct = (premium / base_value) * 100
        
        valuation_table.add_row(
            name,
            role,
            f"{utility:.0f} credits",
            f"+{premium:.0f} ({premium_pct:+.0f}%)"
        )
    
    console.print(valuation_table)
    
    console.print("\n[bold]Insight:[/bold] Same product, different values based on personality!")
    console.print("[dim]- High openness (Alex) values innovation → highest valuation\n- High neuroticism (Charlie) fears risk → lowest valuation\n- Quality-focused (Barbara) willing to pay for excellence[/dim]\n")


def scenario_2_price_negotiation(agents):
    """Scenario 2: Two agents negotiate a price"""
    console.print("\n[bold yellow]═══ SCENARIO 2: Price Negotiation ═══[/bold yellow]\n")
    
    # Setup: Diana (seller) and Alex (buyer)
    seller = agents[3]  # Diana - high agreeableness
    buyer = agents[0]   # Alex - high openness
    
    console.print(f"[bold]{seller.name}[/bold] (seller) negotiates with [bold]{buyer.name}[/bold] (buyer)")
    console.print(f"Product: Custom Software License\n")
    
    # Negotiation parameters
    item = "Custom Software License"
    seller_reserve = 800  # Won't sell below this
    buyer_max = 1500      # Won't pay above this
    
    console.print(f"[dim]Seller's minimum: {seller_reserve} credits\nBuyer's maximum: {buyer_max} credits\nZOPA (Zone of Possible Agreement): {buyer_max - seller_reserve} credits[/dim]\n")
    
    console.print("[bold green]Negotiation in progress...[/bold green]\n")
    
    # Run negotiation
    with console.status("[bold green]Agents negotiating...[/bold green]"):
        result = negotiate_price(
            buyer=buyer,
            seller=seller,
            item=item,
            seller_reserve=seller_reserve,
            buyer_max=buyer_max,
            max_rounds=5
        )
    
    # Display negotiation trajectory
    trajectory_table = Table(title="Negotiation Trajectory", box=box.SIMPLE)
    trajectory_table.add_column("Round", style="cyan")
    trajectory_table.add_column("Seller Ask", style="red")
    trajectory_table.add_column("Buyer Bid", style="green")
    trajectory_table.add_column("Gap", style="yellow")
    
    # Group offers by round
    rounds_data = {}
    for offer in result.offers:
        if offer.round not in rounds_data:
            rounds_data[offer.round] = {}
        rounds_data[offer.round][offer.role] = offer.price
    
    for round_num in sorted(rounds_data.keys()):
        round_offers = rounds_data[round_num]
        seller_ask = round_offers.get("seller", "-")
        buyer_bid = round_offers.get("buyer", "-")
        
        if isinstance(seller_ask, float) and isinstance(buyer_bid, float):
            gap = seller_ask - buyer_bid
            trajectory_table.add_row(
                str(round_num),
                f"{seller_ask:.0f}",
                f"{buyer_bid:.0f}",
                f"{gap:.0f}"
            )
    
    console.print(trajectory_table)
    
    # Display result
    if result.outcome == NegotiationOutcome.SUCCESS:
        console.print(f"\n[bold green]✓ Deal Reached![/bold green]")
        console.print(f"[bold]Final Price:[/bold] {result.final_price:.0f} credits")
        console.print(f"[bold]Rounds:[/bold] {result.rounds_taken}")
        console.print(f"\n[dim]Seller gained: {result.premium:.0f} above minimum\nBuyer saved: {result.savings:.0f} below maximum[/dim]")
    else:
        console.print(f"\n[bold red]✗ No Deal[/bold red]")
        console.print(f"[bold]Outcome:[/bold] {result.outcome.value}")
    
    console.print("\n[bold]Insight:[/bold] Personality shapes negotiation strategy!")
    console.print("[dim]- High agreeableness (Diana) makes larger concessions\n- High openness (Alex) flexible and creative in offers[/dim]\n")
    
    return result


def scenario_3_marketplace(agents):
    """Scenario 3: Multi-agent marketplace with price discovery"""
    console.print("\n[bold yellow]═══ SCENARIO 3: Marketplace Dynamics ═══[/bold yellow]\n")
    
    console.print("Multiple buyers and sellers trade in an open marketplace.\n")
    
    # Split into buyers and sellers
    buyers = agents[:2]   # Alex, Barbara
    sellers = agents[2:]  # Charlie, Diana
    
    console.print(f"[bold]Buyers:[/bold] {', '.join(b.name for b in buyers)}")
    console.print(f"[bold]Sellers:[/bold] {', '.join(s.name for s in sellers)}\n")
    
    console.print("[bold]Product:[/bold] Premium Feature Access")
    console.print("[bold]Base Value:[/bold] 600 credits\n")
    
    console.print("[bold green]Market opening...[/bold green]\n")
    
    # Run market simulation
    with console.status("[bold green]Agents trading...[/bold green]"):
        result = simulate_market(
            buyers=buyers,
            sellers=sellers,
            item="Premium Feature Access",
            base_value=600,
            context={
                "novelty_bonus": 100,
                "quality_premium": 80,
                "description": "Annual premium subscription"
            }
        )
    
    # Display transactions
    if result.transactions:
        trans_table = Table(title="Completed Transactions", box=box.ROUNDED)
        trans_table.add_column("Buyer", style="green")
        trans_table.add_column("Seller", style="red")
        trans_table.add_column("Price", style="yellow")
        
        for trans in result.transactions:
            trans_table.add_row(
                trans.buyer_id,
                trans.seller_id,
                f"{trans.price:.0f} credits"
            )
        
        console.print(trans_table)
        
        # Market statistics
        console.print(f"\n[bold]Market Statistics:[/bold]")
        console.print(f"  Average Price: {result.avg_price:.0f} credits")
        console.print(f"  Price Range: {result.price_range[0]:.0f} - {result.price_range[1]:.0f} credits")
        console.print(f"  Volume: {result.total_volume} units")
        console.print(f"  Active Buyers: {result.active_buyers}/{len(buyers)}")
        console.print(f"  Active Sellers: {result.active_sellers}/{len(sellers)}")
    else:
        console.print("[bold red]No transactions occurred![/bold red]")
        console.print("[dim]Buyers and sellers couldn't agree on price.[/dim]")
    
    # Show unsold and unmatched
    if result.unsold_listings:
        console.print(f"\n[bold yellow]Unsold Listings:[/bold yellow] {len(result.unsold_listings)}")
        for listing in result.unsold_listings:
            console.print(f"  • {listing.seller_id}: {listing.price:.0f} credits (too high)")
    
    if result.unmatched_buyers:
        console.print(f"\n[bold yellow]Unmatched Buyers:[/bold yellow] {', '.join(result.unmatched_buyers)}")
        console.print("[dim]Either couldn't afford or didn't see sufficient value[/dim]")
    
    console.print("\n[bold]Insight:[/bold] Market price emerges from distributed decisions!")
    console.print("[dim]- No central coordinator setting prices\n- Personality diversity creates price variation\n- Supply and demand find equilibrium naturally[/dim]\n")


def scenario_4_demand_curve(agents):
    """Scenario 4: Price sensitivity analysis"""
    console.print("\n[bold yellow]═══ SCENARIO 4: Demand Curve Analysis ═══[/bold yellow]\n")
    
    console.print("How many units would sell at different prices?\n")
    
    buyers = agents  # All agents as potential buyers
    item = "Cloud Computing Credits"
    
    console.print(f"[bold]Analyzing:[/bold] {item}")
    console.print(f"[bold]Buyers:[/bold] {len(buyers)} agents\n")
    
    # Analyze demand at different prices
    demand = analyze_price_sensitivity(
        buyers=buyers,
        sellers=[],  # Not needed for this analysis
        item=item,
        price_range=(100, 1000),
        steps=9
    )
    
    # Display demand curve
    demand_table = Table(title="Demand Schedule", box=box.SIMPLE)
    demand_table.add_column("Price", style="yellow")
    demand_table.add_column("Quantity Demanded", style="green")
    demand_table.add_column("Visual", style="cyan")
    
    max_qty = max(demand.values()) if demand else 1
    
    for price in sorted(demand.keys()):
        qty = demand[price]
        bar = "█" * int((qty / max_qty) * 20) if max_qty > 0 else ""
        
        demand_table.add_row(
            f"{price:.0f} credits",
            str(qty),
            bar
        )
    
    console.print(demand_table)
    
    # Find optimal price (maximize revenue)
    revenues = {price: price * qty for price, qty in demand.items()}
    optimal_price = max(revenues, key=revenues.get)
    optimal_revenue = revenues[optimal_price]
    optimal_qty = demand[optimal_price]
    
    console.print(f"\n[bold]Revenue Maximization:[/bold]")
    console.print(f"  Optimal Price: {optimal_price:.0f} credits")
    console.print(f"  Quantity: {optimal_qty} units")
    console.print(f"  Total Revenue: {optimal_revenue:.0f} credits")
    
    console.print("\n[bold]Insight:[/bold] Demand curves emerge from agent psychology!")
    console.print("[dim]- Lower prices → more buyers (affordability)\n- Higher prices → fewer buyers (insufficient value)\n- Sweet spot balances volume and margin[/dim]\n")


def display_key_insights():
    """Display key insights from agent economy"""
    console.print("\n[bold yellow]═══ KEY INSIGHTS ═══[/bold yellow]\n")
    
    insights = [
        "[bold green]✓[/bold green] [bold]Differential Valuation:[/bold] Same product, different values based on personality",
        "[bold green]✓[/bold green] [bold]Negotiation Dynamics:[/bold] Personality traits shape bargaining strategies",
        "[bold green]✓[/bold green] [bold]Market Equilibrium:[/bold] Prices emerge without central coordinator",
        "[bold green]✓[/bold green] [bold]Demand Curves:[/bold] Psychology + budget constraints = market behavior",
        "[bold yellow]→[/bold yellow] [bold]Real-World Applications:[/bold] Pricing optimization, negotiation training, market simulation"
    ]
    
    for insight in insights:
        console.print(f"  {insight}")
    
    console.print("\n[dim]Traditional personas are static preferences.\n"
                 "Economic agents make real tradeoffs under constraints.[/dim]\n")


def main():
    print_header()
    
    # Create agents
    agents = create_economic_agents()
    
    # Run scenarios
    scenario_1_utility_valuation(agents)
    scenario_2_price_negotiation(agents)
    scenario_3_marketplace(agents)
    scenario_4_demand_curve(agents)
    
    # Show insights
    display_key_insights()
    
    console.print("\n[bold cyan]Next: Article 4 - Algorithmic Evolution[/bold cyan]")
    console.print("[dim]Where agent behaviors drift and adapt over time.[/dim]\n")


if __name__ == "__main__":
    main()
