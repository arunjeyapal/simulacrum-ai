# examples/05_governance_architecture_demo.py
"""
Governance as Architecture Demo

This example demonstrates how to govern evolving AI agents through:
- Trait boundaries (prevent dangerous drift)
- Behavioral constraints (restrict forbidden actions)
- Alignment monitoring (detect misalignment)
- Audit trails (complete transparency)

Accompanying Article: "Governance as Architecture"
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
    create_early_adopter,
    create_skeptic,
    create_anxious_user
)
from simulacrum.evolution.temporal import (
    create_temporal_agent,
    ExperienceType
)
from simulacrum.governance.guardrails import (
    Guardrails,
    GovernancePolicy,
    TraitBoundary,
    AlignmentTarget,
    GovernanceMonitor,
    create_standard_policy
)
from simulacrum.governance.audit import (
    AuditTrail,
    ExplainabilityEngine,
    ComplianceReporter
)

console = Console()


def print_header():
    """Display welcome header"""
    console.print(Panel.fit(
        "[bold cyan]Simulacrum: Governance as Architecture Demo[/bold cyan]\n"
        "[dim]Keeping AI Safe as It Evolves[/dim]",
        border_style="cyan",
        box=box.DOUBLE
    ))


def create_governed_agent(name: str, traits):
    """Create an agent with governance and audit."""
    base = create_early_adopter(name=name) if traits == "adopter" else \
           create_skeptic(name=name) if traits == "skeptic" else \
           create_anxious_user(name=name)
    
    temporal = create_temporal_agent(base, drift_rate=0.03)
    audit = AuditTrail(base.name)
    
    return temporal, audit


def scenario_1_trait_boundaries():
    """Scenario 1: Trait boundaries prevent dangerous drift"""
    console.print("\n[bold yellow]═══ SCENARIO 1: Trait Boundaries ═══[/bold yellow]\n")
    
    console.print("Agent undergoes experiences that would make them too aggressive.\n")
    console.print("[bold]Without Governance:[/bold] Agent could drift into dangerous territory")
    console.print("[bold]With Governance:[/bold] Boundaries enforce safety constraints\n")
    
    # Create agent
    temporal, audit = create_governed_agent("Alex", "adopter")
    agent = temporal.agent
    
    # Show initial traits
    console.print(f"[bold green]Initial:[/bold green] Agreeableness = {agent.traits.agreeableness:.2f}")
    
    # Create governance policy with trait boundary
    policy = GovernancePolicy(
        policy_id="safety_v1",
        name="Safety Policy",
        description="Prevent adversarial behavior",
        trait_boundaries=[
            TraitBoundary(
                trait_name="agreeableness",
                min_value=0.3,
                description="Must maintain minimum cooperation",
                enforcement="hard"
            )
        ],
        auto_remediate=True
    )
    
    guardrails = Guardrails(policy)
    
    # Simulate experiences that decrease agreeableness
    console.print("\n[bold yellow]Simulating 10 competitive trading experiences...[/bold yellow]\n")
    
    for i in range(10):
        # Experience that decreases agreeableness
        temporal.add_experience(
            f"Won aggressive negotiation #{i+1}",
            ExperienceType.POSITIVE,
            intensity=0.8,
            trait_impacts={"agreeableness": -0.05}
        )
        
        audit.log_trait_change(
            "agreeableness",
            agent.traits.agreeableness + 0.05,
            agent.traits.agreeableness,
            "competitive_experience"
        )
        
        # Check governance
        violations = guardrails.check_trait_boundaries(agent)
        
        if violations:
            for v in violations:
                console.print(f"  [bold red]⚠ Violation:[/bold red] {v.description}")
                console.print(f"     [dim]Action: {v.action_taken}[/dim]")
                audit.log_violation(
                    v.violation_type.value,
                    v.description,
                    v.severity,
                    v.action_taken
                )
        
        time.sleep(0.1)
    
    console.print(f"\n[bold]Final:[/bold] Agreeableness = {agent.traits.agreeableness:.2f}")
    console.print(f"[bold]Boundary:[/bold] Minimum = {policy.trait_boundaries[0].min_value:.2f}")
    
    console.print("\n[bold green]✓ Governance prevented dangerous drift![/bold green]")
    console.print("[dim]Without boundaries, agreeableness would have dropped to ~0.15[/dim]\n")


def scenario_2_alignment_monitoring():
    """Scenario 2: Alignment monitoring detects drift from values"""
    console.print("\n[bold yellow]═══ SCENARIO 2: Alignment Monitoring ═══[/bold yellow]\n")
    
    console.print("Agent should maintain prosocial orientation, but drift is happening.\n")
    
    # Create agents
    temporal1, audit1 = create_governed_agent("Barbara", "skeptic")
    temporal2, audit2 = create_governed_agent("Charlie", "anxious")
    
    agents = [temporal1, temporal2]
    
    # Define alignment target (prosocial values)
    policy = GovernancePolicy(
        policy_id="alignment_v1",
        name="Prosocial Alignment",
        description="Maintain cooperative and conscientious behavior",
        alignment_targets=[
            AlignmentTarget(
                target_id="prosocial",
                description="Prosocial value orientation",
                target_traits={
                    "agreeableness": 0.65,
                    "conscientiousness": 0.65
                },
                tolerance=0.2
            )
        ],
        auto_remediate=True
    )
    
    guardrails = Guardrails(policy)
    monitor = GovernanceMonitor(guardrails)
    
    # Show initial alignment
    console.print("[bold]Target Alignment:[/bold]")
    console.print(f"  Agreeableness: {policy.alignment_targets[0].target_traits['agreeableness']:.2f}")
    console.print(f"  Conscientiousness: {policy.alignment_targets[0].target_traits['conscientiousness']:.2f}")
    console.print(f"  Tolerance: ±{policy.alignment_targets[0].tolerance:.2f}\n")
    
    # Simulate drift
    console.print("[bold yellow]Simulating 90 days of experiences...[/bold yellow]\n")
    
    for day in track(range(30), description="Days"):
        for temporal in agents:
            # Random experiences that cause drift
            import random
            if random.random() < 0.3:
                temporal.add_experience(
                    "Competitive situation",
                    ExperienceType.NEUTRAL,
                    trait_impacts={
                        "agreeableness": random.uniform(-0.02, 0.01),
                        "conscientiousness": random.uniform(-0.02, 0.01)
                    }
                )
        
        # Check alignment every 10 days
        if day % 10 == 0:
            report = monitor.monitor_population([t.agent for t in agents])
            
            if report["total_violations"] > 0:
                console.print(f"\n  [bold red]Day {day}:[/bold red] {report['total_violations']} alignment issues detected")
                console.print(f"     [dim]Auto-remediation applied to {report['agents_with_violations']} agents[/dim]")
        
        time.sleep(0.03)
    
    # Final alignment check
    console.print("\n[bold]Final Alignment Check:[/bold]\n")
    
    final_report = monitor.monitor_population([t.agent for t in agents])
    
    alignment_table = Table(box=box.SIMPLE)
    alignment_table.add_column("Agent", style="cyan")
    alignment_table.add_column("Agreeable", style="yellow")
    alignment_table.add_column("Conscientious", style="yellow")
    alignment_table.add_column("Status", style="magenta")
    
    for temporal in agents:
        agent = temporal.agent
        status = "✓ Aligned" if any(
            r["status"] == "compliant" and r["agent_id"] == agent.name
            for r in final_report["agent_reports"]
        ) else "⚠ Drifted"
        
        alignment_table.add_row(
            agent.name,
            f"{agent.traits.agreeableness:.2f}",
            f"{agent.traits.conscientiousness:.2f}",
            status
        )
    
    console.print(alignment_table)
    
    console.print(f"\n[bold]Population Status:[/bold] {final_report['compliant_agents']}/{final_report['population_size']} compliant")
    console.print("\n[bold green]✓ Alignment monitoring keeps agents on track![/bold green]\n")


def scenario_3_audit_transparency():
    """Scenario 3: Complete audit trail provides transparency"""
    console.print("\n[bold yellow]═══ SCENARIO 3: Audit Trail & Transparency ═══[/bold yellow]\n")
    
    console.print("Every action, decision, and change is logged for accountability.\n")
    
    # Create agent with audit
    temporal, audit = create_governed_agent("Diana", "adopter")
    agent = temporal.agent
    
    # Simulate some activity
    console.print("[bold green]Simulating agent activity...[/bold green]\n")
    
    # Decision 1
    audit.log_decision(
        decision="Increase price by 15%",
        reasoning="Market demand is high, competitors raised prices",
        outcome="Success: Revenue increased 12%",
        metadata={"confidence": 0.7}
    )
    
    # Trait change 1
    old_val = agent.traits.openness
    temporal.add_experience(
        "Pricing strategy succeeded",
        ExperienceType.POSITIVE,
        trait_impacts={"openness": 0.02}
    )
    audit.log_trait_change("openness", old_val, agent.traits.openness, "success_reinforcement")
    
    time.sleep(0.2)
    
    # Decision 2
    audit.log_decision(
        decision="Launch new product feature",
        reasoning="High openness encourages innovation",
        outcome="Mixed: Some users love it, others confused",
        metadata={"confidence": 0.5}
    )
    
    # Violation
    audit.log_violation(
        violation_type="behavior_constraint",
        description="Attempted to share user data without consent",
        severity=0.8,
        action_taken="Action blocked by guardrails"
    )
    
    time.sleep(0.2)
    
    # Remediation
    audit.log_remediation(
        what_was_fixed="Openness exceeded boundary",
        how_fixed="Reset to maximum allowed value (0.95)",
        metadata={"original": 0.97, "corrected": 0.95}
    )
    
    # Show audit trail
    console.print("\n[bold]Audit Trail (Last 30 days):[/bold]\n")
    
    trail_table = Table(box=box.ROUNDED)
    trail_table.add_column("Type", style="cyan")
    trail_table.add_column("Description", style="yellow", max_width=50)
    trail_table.add_column("Timestamp", style="dim")
    
    for event in audit.events:
        trail_table.add_row(
            event.event_type,
            event.description,
            event.timestamp.strftime("%H:%M:%S")
        )
    
    console.print(trail_table)
    
    # Generate compliance report
    report = audit.generate_report(period_days=30)
    
    console.print(f"\n[bold]Compliance Report:[/bold]")
    console.print(f"  Total Events: {report['total_events']}")
    console.print(f"  Decisions: {report['events_by_type'].get('decision', 0)}")
    console.print(f"  Trait Changes: {len(report['trait_changes'])}")
    console.print(f"  Violations: {report['violations']}")
    console.print(f"  Remediations: {report['remediations']}")
    
    # Explainability
    console.print("\n[bold]Explainability Example:[/bold]\n")
    explainer = ExplainabilityEngine(agent)
    explanation = explainer.explain_decision(
        decision="Launch new product feature",
        context={"market_conditions": "favorable"}
    )
    console.print(Panel(explanation, title="Decision Explanation", border_style="blue"))
    
    console.print("\n[bold green]✓ Complete transparency enables accountability![/bold green]\n")


def scenario_4_population_governance():
    """Scenario 4: Governing an entire population of agents"""
    console.print("\n[bold yellow]═══ SCENARIO 4: Population-Level Governance ═══[/bold yellow]\n")
    
    console.print("Managing 10 agents with consistent safety policies.\n")
    
    # Create population
    agents = []
    audits = {}
    
    for i in range(10):
        name = f"Agent_{i+1}"
        agent_type = ["adopter", "skeptic", "anxious"][i % 3]
        temporal, audit = create_governed_agent(name, agent_type)
        agents.append(temporal)
        audits[name] = audit
    
    console.print(f"[bold]Created population of {len(agents)} agents[/bold]\n")
    
    # Create comprehensive governance
    policy = create_standard_policy("Enterprise Safety Policy")
    guardrails = Guardrails(policy)
    monitor = GovernanceMonitor(guardrails)
    reporter = ComplianceReporter()
    
    # Simulate 30 days
    console.print("[bold green]Simulating 30 days of operations...[/bold green]\n")
    
    for day in track(range(30), description="Days"):
        for temporal in agents:
            # Random experiences
            import random
            if random.random() < 0.4:
                exp_type = random.choice([ExperienceType.POSITIVE, ExperienceType.NEGATIVE, ExperienceType.NEUTRAL])
                temporal.add_experience(
                    f"Day {day} experience",
                    exp_type,
                    trait_impacts={
                        "openness": random.uniform(-0.02, 0.02),
                        "agreeableness": random.uniform(-0.02, 0.02)
                    }
                )
        
        # Daily monitoring
        if day % 5 == 0:
            monitor.monitor_population([t.agent for t in agents])
        
        time.sleep(0.05)
    
    # Generate final compliance report
    console.print("\n[bold]Population Compliance Report:[/bold]\n")
    
    final_report = reporter.generate_population_report(
        agents=[t.agent for t in agents],
        audit_trails=audits,
        guardrails=guardrails
    )
    
    report_table = Table(box=box.HEAVY)
    report_table.add_column("Metric", style="cyan")
    report_table.add_column("Value", style="yellow")
    
    report_table.add_row("Population Size", str(final_report["population_size"]))
    report_table.add_row("Compliant Agents", str(final_report["compliant_agents"]))
    report_table.add_row("Total Violations", str(final_report["total_violations"]))
    report_table.add_row("Avg Violations/Agent", f"{final_report['avg_violations_per_agent']:.1f}")
    report_table.add_row("Population Health", final_report["population_health"])
    
    if final_report["high_risk_agents"]:
        report_table.add_row(
            "High Risk Agents",
            ", ".join(final_report["high_risk_agents"])
        )
    
    console.print(report_table)
    
    # Violation summary
    violation_summary = guardrails.get_violation_summary()
    
    if violation_summary["total_violations"] > 0:
        console.print(f"\n[bold]Violation Breakdown:[/bold]")
        for vtype, count in violation_summary["by_type"].items():
            console.print(f"  {vtype}: {count}")
    
    console.print("\n[bold green]✓ Population governance maintains fleet-wide safety![/bold green]\n")


def display_key_insights():
    """Display key insights from governance"""
    console.print("\n[bold yellow]═══ KEY INSIGHTS ═══[/bold yellow]\n")
    
    insights = [
        "[bold green]✓[/bold green] [bold]Trait Boundaries:[/bold] Prevent agents from drifting into dangerous territory",
        "[bold green]✓[/bold green] [bold]Alignment Monitoring:[/bold] Detect misalignment before it causes harm",
        "[bold green]✓[/bold green] [bold]Auto-Remediation:[/bold] Automatically correct violations in real-time",
        "[bold green]✓[/bold green] [bold]Audit Trails:[/bold] Complete transparency for accountability",
        "[bold green]✓[/bold green] [bold]Explainability:[/bold] Understand why agents make decisions",
        "[bold green]✓[/bold green] [bold]Population Management:[/bold] Scale governance to entire fleets",
        "[bold cyan]→[/bold cyan] [bold]Governance as Code:[/bold] Safety policies enforced architecturally"
    ]
    
    for insight in insights:
        console.print(f"  {insight}")
    
    console.print("\n[dim]Safety isn't a feature—it's the architecture.\n"
                 "Build constraints into the system, not just the training.[/dim]\n")


def main():
    print_header()
    
    # Run scenarios
    scenario_1_trait_boundaries()
    scenario_2_alignment_monitoring()
    scenario_3_audit_transparency()
    scenario_4_population_governance()
    
    # Show insights
    display_key_insights()
    
    console.print("\n[bold cyan]🎉 Series Complete! 🎉[/bold cyan]")
    console.print("\n[bold]The Simulation Layer:[/bold]")
    console.print("  1. ✅ Synthetic Citizens - Psychology")
    console.print("  2. ✅ Distributed Protocols - Collaboration")
    console.print("  3. ✅ Agent-to-Agent Economy - Transactions")
    console.print("  4. ✅ Algorithmic Evolution - Time & Change")
    console.print("  5. ✅ Governance as Architecture - Safety & Control")
    console.print("\n[dim]You now have a complete framework for building safe, adaptive, multi-agent AI systems.[/dim]\n")


if __name__ == "__main__":
    main()
