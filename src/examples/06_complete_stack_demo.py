
# examples/06_complete_stack_demo.py
"""
Complete Stack Integration Demo

This example demonstrates ALL 5 LAYERS working together in a realistic scenario:
A product team using AI agents to make decisions about a new feature launch.

SCENARIO:
- Layer 1 (Psychology): Diverse team members with different personalities
- Layer 2 (Protocols): Team votes on decisions using consensus
- Layer 3 (Economy): Budget constraints and cost-benefit analysis
- Layer 4 (Evolution): Team learns from past launches and adapts
- Layer 5 (Governance): Safety constraints prevent risky decisions

This is the COMPLETE framework in action.

Accompanying Article: "The Complete Stack: A Real-World Example"
"""

import sys
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.progress import track
import time
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

# Layer 1: Individual Psychology
from simulacrum.agents.persona import (
    PsychologicalProfile,
    Citizen
)

# Layer 2: Distributed Protocols
from simulacrum.protocols.voting import quick_vote

# Layer 3: Economic Behavior
from simulacrum.economy.wallet import create_economic_citizen
from simulacrum.economy.marketplace import simulate_market

# Layer 4: Temporal Dynamics
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

# Layer 5: Governance
from simulacrum.governance.guardrails import (
    Guardrails,
    GovernancePolicy,
    TraitBoundary,
    BehaviorConstraint,
    AlignmentTarget,
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
        "[bold cyan]Simulacrum: Complete Stack Demo[/bold cyan]\n"
        "[dim]All 5 Layers Working Together[/dim]\n\n"
        "[yellow]Scenario: Product Team Feature Launch Decision[/yellow]",
        border_style="cyan",
        box=box.DOUBLE
    ))


class ProductTeamMember:
    """Enhanced team member with all 5 layers integrated."""
    
    def __init__(
        self,
        name: str,
        role: str,
        traits: PsychologicalProfile,
        budget: float = 5000
    ):
        # Layer 1: Create base citizen with psychology
        self.citizen = Citizen(name=name, role=role, traits=traits)
        
        # Layer 3: Add economic capabilities
        self.citizen.wallet = create_economic_citizen(
            name, role, traits, budget
        ).wallet
        
        # Layer 4: Add temporal dynamics and learning
        self.temporal = create_temporal_agent(self.citizen, drift_rate=0.02)
        self.learner = create_adaptive_learner(self.citizen, learning_rate=0.15)
        
        # Layer 5: Add governance and audit
        self.audit = AuditTrail(name)
        self.explainer = ExplainabilityEngine(self.citizen)
        
        # Track decisions
        self.decisions_made = []
        self.experiences = []
    
    def make_decision(
        self,
        decision: str,
        context: dict,
        guardrails: Guardrails = None
    ) -> dict:
        """Make a decision using all layers."""
        
        # Layer 1: Consider personality
        personality_influence = self._get_personality_influence(context)
        
        # Layer 3: Consider budget
        economic_feasible = self._check_economic_feasibility(context)
        
        # Layer 4: Apply learned strategies
        learned_strategy = self.learner.get_best_strategy(context.get("type", "general"))
        
        # Layer 5: Check governance constraints
        if guardrails:
            violation = guardrails.check_behavior_constraint(
                self.citizen,
                decision,
                context
            )
            if violation:
                self.audit.log_violation(
                    violation.violation_type.value,
                    violation.description,
                    violation.severity
                )
                return {
                    "decision": "blocked",
                    "reason": "governance_violation",
                    "violation": violation
                }
        
        # Combine all factors
        final_decision = {
            "agent": self.citizen.name,
            "decision": decision,
            "personality_factor": personality_influence,
            "economic_factor": economic_feasible,
            "learned_strategy": learned_strategy.description if learned_strategy else "none",
            "timestamp": datetime.now()
        }
        
        # Layer 5: Log decision
        self.audit.log_decision(
            decision,
            f"Personality: {personality_influence}, Economics: {economic_feasible}",
            metadata=context
        )
        
        self.decisions_made.append(final_decision)
        return final_decision
    
    def _get_personality_influence(self, context: dict) -> str:
        """Layer 1: How personality affects this decision."""
        traits = self.citizen.traits
        
        if context.get("risky", False):
            if traits.openness > 0.7:
                return "enthusiastic (high openness)"
            elif traits.neuroticism > 0.7:
                return "cautious (high neuroticism)"
        
        if context.get("collaborative", False):
            if traits.agreeableness > 0.7:
                return "supportive (high agreeableness)"
        
        return "neutral"
    
    def _check_economic_feasibility(self, context: dict) -> bool:
        """Layer 3: Can we afford this?"""
        cost = context.get("cost", 0)
        return self.citizen.wallet.can_afford(cost)
    
    def learn_from_outcome(self, decision_id: str, outcome: str, reward: float):
        """Layer 4: Learn from decision outcome."""
        # Record outcome
        self.learner.record_outcome(
            decision_id,
            OutcomeType.SUCCESS if reward > 0 else OutcomeType.FAILURE,
            reward=reward
        )
        
        # Add experience that affects traits
        exp_type = ExperienceType.POSITIVE if reward > 0 else ExperienceType.NEGATIVE
        
        trait_impacts = {}
        if reward > 100:
            trait_impacts["openness"] = 0.02  # Success breeds confidence
        elif reward < -100:
            trait_impacts["neuroticism"] = 0.02  # Failure breeds caution
        
        experience = self.temporal.add_experience(
            f"Decision outcome: {outcome}",
            exp_type,
            intensity=min(1.0, abs(reward) / 500),
            trait_impacts=trait_impacts
        )
        
        self.experiences.append(experience)
        
        # Log to audit trail
        self.audit.log_trait_change(
            "openness" if reward > 0 else "neuroticism",
            self.citizen.traits.openness if reward > 0 else self.citizen.traits.neuroticism,
            self.citizen.traits.openness + trait_impacts.get("openness", 0) if reward > 0 
                else self.citizen.traits.neuroticism + trait_impacts.get("neuroticism", 0),
            "outcome_learning"
        )


def create_product_team():
    """Create a diverse product team with all capabilities."""
    console.print("\n[bold yellow]Creating Product Team...[/bold yellow]\n")
    
    team = [
        # Product Manager - High openness, loves innovation
        ProductTeamMember(
            "Sarah",
            "Product Manager",
            PsychologicalProfile(
                openness=0.9,
                conscientiousness=0.7,
                extraversion=0.8,
                agreeableness=0.6,
                neuroticism=0.3
            ),
            budget=10000
        ),
        
        # Engineer - High conscientiousness, detail-oriented
        ProductTeamMember(
            "David",
            "Senior Engineer",
            PsychologicalProfile(
                openness=0.6,
                conscientiousness=0.9,
                extraversion=0.4,
                agreeableness=0.7,
                neuroticism=0.4
            ),
            budget=8000
        ),
        
        # Designer - Creative but cautious
        ProductTeamMember(
            "Maria",
            "UX Designer",
            PsychologicalProfile(
                openness=0.85,
                conscientiousness=0.7,
                extraversion=0.6,
                agreeableness=0.8,
                neuroticism=0.5
            ),
            budget=7000
        ),
        
        # Finance - Risk averse, data-driven
        ProductTeamMember(
            "James",
            "Finance Lead",
            PsychologicalProfile(
                openness=0.4,
                conscientiousness=0.9,
                extraversion=0.5,
                agreeableness=0.6,
                neuroticism=0.7
            ),
            budget=15000
        )
    ]
    
    # Display team
    team_table = Table(title="Product Team", box=box.ROUNDED)
    team_table.add_column("Name", style="cyan")
    team_table.add_column("Role", style="magenta")
    team_table.add_column("Key Traits", style="yellow")
    team_table.add_column("Budget", style="green")
    
    for member in team:
        traits = member.citizen.traits
        key_trait = max(
            [("Open", traits.openness),
             ("Conscientious", traits.conscientiousness),
             ("Anxious", traits.neuroticism),
             ("Agreeable", traits.agreeableness)],
            key=lambda x: x[1]
        )[0]
        
        team_table.add_row(
            member.citizen.name,
            member.citizen.role,
            f"{key_trait} ({max(traits.openness, traits.conscientiousness, traits.neuroticism, traits.agreeableness):.2f})",
            f"${member.citizen.wallet.balance:,.0f}"
        )
    
    console.print(team_table)
    console.print()
    
    return team


def setup_governance(team):
    """Layer 5: Set up governance for the team."""
    console.print("[bold yellow]Setting up Governance Framework...[/bold yellow]\n")
    
    # Define what's not allowed
    def no_budget_overruns(agent, action, params):
        """Don't allow spending beyond team budget."""
        if action == "approve_budget":
            cost = params.get("cost", 0)
            total_budget = sum(m.citizen.wallet.balance for m in team)
            return cost <= total_budget * 0.5  # Max 50% of total budget
        return True
    
    def no_high_risk_without_data(agent, action, params):
        """Risky decisions require data backing."""
        if action == "approve_feature":
            risk_level = params.get("risk", "low")
            has_data = params.get("has_research", False)
            
            if risk_level == "high":
                return has_data  # High risk needs research
        return True
    
    policy = GovernancePolicy(
        policy_id="product_team_v1",
        name="Product Team Safety Policy",
        description="Ensures responsible feature development",
        trait_boundaries=[
            # Don't let anyone become too risk-seeking
            TraitBoundary(
                trait_name="openness",
                max_value=0.95,
                description="Prevent reckless innovation"
            ),
            # Don't let anyone become too anxious
            TraitBoundary(
                trait_name="neuroticism",
                max_value=0.85,
                description="Prevent decision paralysis"
            )
        ],
        behavior_constraints=[
            BehaviorConstraint(
                constraint_id="budget_limit",
                description="No budget overruns",
                validator=no_budget_overruns
            ),
            BehaviorConstraint(
                constraint_id="risk_requires_data",
                description="High-risk features need research",
                validator=no_high_risk_without_data
            )
        ],
        alignment_targets=[
            AlignmentTarget(
                target_id="user_focused",
                description="Stay user-focused",
                target_traits={
                    "agreeableness": 0.7,  # Collaborative
                    "conscientiousness": 0.7  # Quality-focused
                },
                tolerance=0.25
            )
        ],
        auto_remediate=True
    )
    
    guardrails = Guardrails(policy)
    
    console.print(f"✅ Governance policy created: {policy.name}")
    console.print(f"   - {len(policy.trait_boundaries)} trait boundaries")
    console.print(f"   - {len(policy.behavior_constraints)} behavioral constraints")
    console.print(f"   - {len(policy.alignment_targets)} alignment targets\n")
    
    return guardrails


def scenario_feature_launch_decision(team, guardrails):
    """Complete scenario: Team decides whether to launch a feature."""
    console.print("\n[bold yellow]═══ SCENARIO: AI-Powered Analytics Feature ═══[/bold yellow]\n")
    
    console.print("The team must decide: Should we launch an AI-powered analytics feature?\n")
    
    # Feature details
    feature_context = {
        "name": "AI-Powered Customer Analytics",
        "cost": 25000,
        "risk": "high",
        "potential_revenue": 100000,
        "has_research": True,  # We did user research
        "development_time": "3 months"
    }
    
    console.print("[bold]Feature Details:[/bold]")
    console.print(f"  Cost: ${feature_context['cost']:,}")
    console.print(f"  Risk Level: {feature_context['risk']}")
    console.print(f"  Potential Revenue: ${feature_context['potential_revenue']:,}")
    console.print(f"  User Research: {'✓ Yes' if feature_context['has_research'] else '✗ No'}")
    console.print(f"  Timeline: {feature_context['development_time']}\n")
    
    # Phase 1: Individual Analysis (Layer 1 + 3 + 4)
    console.print("[bold green]Phase 1: Individual Team Member Analysis[/bold green]\n")
    
    analysis_table = Table(box=box.SIMPLE)
    analysis_table.add_column("Member", style="cyan")
    analysis_table.add_column("Personality", style="yellow")
    analysis_table.add_column("Can Afford?", style="green")
    analysis_table.add_column("Past Experience", style="magenta")
    
    for member in team:
        # Personality influence
        personality = member._get_personality_influence(feature_context)
        
        # Economic check
        can_afford = "✓" if member._check_economic_feasibility(feature_context) else "✗"
        
        # Learned strategies
        past_strategy = member.learner.get_best_strategy("feature_launch")
        past_exp = f"{past_strategy.success_rate:.0%}" if past_strategy else "No data"
        
        analysis_table.add_row(
            member.citizen.name,
            personality,
            can_afford,
            past_exp
        )
    
    console.print(analysis_table)
    console.print()
    
    # Phase 2: Team Vote (Layer 2)
    console.print("[bold green]Phase 2: Team Vote on Feature[/bold green]\n")
    
    # Layer 5: Check governance before vote
    console.print("[dim]Checking governance constraints...[/dim]")
    
    violation = guardrails.policy.behavior_constraints[1].validator(
        team[0].citizen,
        "approve_feature",
        feature_context
    )
    
    if not violation:
        console.print("[bold red]⚠️  Governance Alert: High-risk feature without research data![/bold red]\n")
        console.print("[dim]Proceeding anyway since has_research=True[/dim]\n")
    
    # Conduct vote
    citizens = [m.citizen for m in team]
    vote_result = quick_vote(
        citizens,
        "Approve AI-Powered Analytics feature?",
        ["Approve", "Reject", "Need More Data"]
    )
    
    console.print(f"\n[bold]Vote Result:[/bold] {vote_result.winner}")
    console.print(f"  Approve: {vote_result.vote_counts.get('Approve', 0)}")
    console.print(f"  Reject: {vote_result.vote_counts.get('Reject', 0)}")
    console.print(f"  Need More Data: {vote_result.vote_counts.get('Need More Data', 0)}\n")
    
    # Phase 3: Decision Execution (If approved)
    if vote_result.winner == "Approve":
        console.print("[bold green]Phase 3: Feature Approved - Executing Decision[/bold green]\n")
        
        # Log decisions for all team members
        for member in team:
            decision = member.make_decision(
                "launch_ai_analytics",
                feature_context,
                guardrails
            )
            
            # Record the decision for learning
            dec = member.learner.record_decision(
                context="feature_launch",
                choice="approve_high_risk_ai",
                reasoning=f"Team voted {vote_result.winner}",
                confidence=0.7
            )
        
        # Simulate launch outcome (3 months later)
        console.print("[bold]⏰ 3 Months Later...[/bold]\n")
        time.sleep(0.5)
        
        # Simulate success (positive outcome)
        import random
        success_prob = 0.7  # 70% chance of success given research
        actual_revenue = random.randint(80000, 120000) if random.random() < success_prob else random.randint(10000, 30000)
        
        was_success = actual_revenue >= 80000
        
        if was_success:
            console.print(f"[bold green]✓ Success![/bold green] Feature generated ${actual_revenue:,} in revenue")
            console.print(f"  ROI: {((actual_revenue - feature_context['cost']) / feature_context['cost'] * 100):.0f}%\n")
        else:
            console.print(f"[bold red]✗ Underperformed[/bold red] Feature only generated ${actual_revenue:,}")
            console.print(f"  Loss: ${feature_context['cost'] - actual_revenue:,}\n")
        
        # Phase 4: Team Learning (Layer 4)
        console.print("[bold green]Phase 4: Team Learning from Outcome[/bold green]\n")
        
        reward = actual_revenue - feature_context['cost']
        
        learning_table = Table(box=box.ROUNDED)
        learning_table.add_column("Member", style="cyan")
        learning_table.add_column("Trait Change", style="yellow")
        learning_table.add_column("Lesson Learned", style="magenta")
        
        for member in team:
            old_openness = member.citizen.traits.openness
            
            # Learn from outcome
            member.learn_from_outcome(
                member.learner.decisions[-1].id if member.learner.decisions else "dec_1",
                "success" if was_success else "underperformed",
                reward / len(team)
            )
            
            new_openness = member.citizen.traits.openness
            trait_change = f"{'↑' if new_openness > old_openness else '↓'} {abs(new_openness - old_openness):.3f}"
            
            # Get learned strategy
            best_strategy = member.learner.get_best_strategy("feature_launch")
            lesson = best_strategy.description if best_strategy else "First experience"
            
            learning_table.add_row(
                member.citizen.name,
                trait_change,
                lesson
            )
        
        console.print(learning_table)
        console.print()
        
        # Phase 5: Governance Check (Layer 5)
        console.print("[bold green]Phase 5: Post-Launch Governance Review[/bold green]\n")
        
        monitor_table = Table(box=box.SIMPLE)
        monitor_table.add_column("Member", style="cyan")
        monitor_table.add_column("Compliance", style="green")
        monitor_table.add_column("Violations", style="red")
        
        for member in team:
            # Check trait boundaries
            violations = guardrails.check_trait_boundaries(member.citizen)
            
            # Check alignment
            alignment_violations = guardrails.check_alignment(member.citizen)
            violations.extend(alignment_violations)
            
            status = "✓ Compliant" if len(violations) == 0 else f"⚠️  {len(violations)} issues"
            violation_desc = ", ".join([v.description for v in violations[:2]]) if violations else "-"
            
            monitor_table.add_row(
                member.citizen.name,
                status,
                violation_desc if violations else "-"
            )
        
        console.print(monitor_table)
        console.print()
        
        # Generate compliance report
        reporter = ComplianceReporter()
        audits = {m.citizen.name: m.audit for m in team}
        
        compliance_report = reporter.generate_population_report(
            [m.citizen for m in team],
            audits,
            guardrails
        )
        
        console.print(f"[bold]Team Compliance Status:[/bold] {compliance_report['population_health']}")
        console.print(f"  Compliant Members: {compliance_report['compliant_agents']}/{len(team)}")
        console.print(f"  Total Violations: {compliance_report['total_violations']}\n")
        
        return was_success
    else:
        console.print(f"[bold yellow]Feature rejected by team vote.[/bold yellow]\n")
        return False


def display_final_summary(team, guardrails):
    """Display complete summary showing all 5 layers."""
    console.print("\n[bold yellow]═══ COMPLETE STACK SUMMARY ═══[/bold yellow]\n")
    
    # Summary table
    summary_table = Table(title="Final Team State (All 5 Layers)", box=box.HEAVY)
    summary_table.add_column("Member", style="cyan")
    summary_table.add_column("Openness", style="yellow")
    summary_table.add_column("Budget", style="green")
    summary_table.add_column("Decisions", style="magenta")
    summary_table.add_column("Experiences", style="blue")
    summary_table.add_column("Violations", style="red")
    
    for member in team:
        violations = guardrails.check_trait_boundaries(member.citizen)
        
        summary_table.add_row(
            member.citizen.name,
            f"{member.citizen.traits.openness:.3f}",
            f"${member.citizen.wallet.balance:,.0f}",
            str(len(member.decisions_made)),
            str(len(member.experiences)),
            str(len(violations))
        )
    
    console.print(summary_table)
    
    # Show what each layer contributed
    console.print("\n[bold]Layers in Action:[/bold]\n")
    
    contributions = [
        "🧠 [bold]Layer 1 (Psychology):[/bold] Different personalities led to different risk assessments",
        "🗳️  [bold]Layer 2 (Protocols):[/bold] Team reached consensus through structured voting",
        "💰 [bold]Layer 3 (Economy):[/bold] Budget constraints influenced feasibility analysis",
        "📈 [bold]Layer 4 (Evolution):[/bold] Team learned from outcome, traits evolved",
        "🛡️  [bold]Layer 5 (Governance):[/bold] Safety constraints prevented risky decisions without data"
    ]
    
    for contribution in contributions:
        console.print(f"  {contribution}")
    
    console.print("\n[bold green]✓ All 5 layers worked together seamlessly![/bold green]\n")


def main():
    print_header()
    
    # Create team with all capabilities
    team = create_product_team()
    
    # Set up governance
    guardrails = setup_governance(team)
    
    # Run complete scenario
    success = scenario_feature_launch_decision(team, guardrails)
    
    # Show final summary
    display_final_summary(team, guardrails)
    
    console.print("\n[bold cyan]🎉 Complete Stack Demo Complete! 🎉[/bold cyan]")
    console.print("\n[dim]This demo showed all 5 layers working together:[/dim]")
    console.print("[dim]  • Individual psychology shaped preferences[/dim]")
    console.print("[dim]  • Team protocols enabled collective decisions[/dim]")
    console.print("[dim]  • Economic constraints grounded choices in reality[/dim]")
    console.print("[dim]  • Temporal dynamics enabled learning and growth[/dim]")
    console.print("[dim]  • Governance ensured safety throughout[/dim]")
    console.print("\n[dim]This is the power of The Simulation Layer.[/dim]\n")


if __name__ == "__main__":
    main()
