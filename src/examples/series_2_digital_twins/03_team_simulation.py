# examples/series_2_digital_twins/03_team_simulation.py
"""
Team Digital Twin Example

Demonstrates simulating team decisions, predicting conflicts,
and optimizing collaboration using team digital twins.

Prerequisites:
    export OPENAI_API_KEY="sk-..."  # or GEMINI_API_KEY
    pip install openai  # or google-generativeai

Run:
    python 03_team_simulation.py
"""

from simulacrum import (
    use_openai,
    quick_twin,
    create_team_twin,
    print_config
)


def example_1_simple_team_decision():
    """Example 1: Basic team decision simulation."""
    print("═══ Example 1: Team Decision Simulation ═══\n")
    
    # Create team members with different personalities
    alice = quick_twin(
        openness=0.9,           # Very innovative
        conscientiousness=0.7,   # Organized
        extraversion=0.6,        # Moderately social
        agreeableness=0.5,       # Balanced
        neuroticism=0.3,         # Calm
        name="Alice (Innovator)"
    )
    
    bob = quick_twin(
        openness=0.3,            # Traditional
        conscientiousness=0.8,   # Very organized
        extraversion=0.4,        # Introverted
        agreeableness=0.7,       # Cooperative
        neuroticism=0.6,         # Anxious
        name="Bob (Cautious)"
    )
    
    carol = quick_twin(
        openness=0.6,            # Moderate
        conscientiousness=0.5,   # Balanced
        extraversion=0.8,        # Very social
        agreeableness=0.8,       # Very cooperative
        neuroticism=0.4,         # Stable
        name="Carol (Collaborator)"
    )
    
    # Create team
    team = create_team_twin([alice, bob, carol], name="Product Team")
    
    print(f"Created: {team}\n")
    
    # Simulate team decision
    decision = team.simulate_team_decision(
        "Launch AI feature with $25K development cost?",
        context={
            "budget": 100000,
            "expected_revenue": 50000,
            "risk_level": "medium",
            "timeline": "3 months"
        },
        voting_method="majority"
    )
    
    print("🎯 Team Decision:")
    print(f"   Outcome: {decision.outcome}")
    print(f"   Consensus: {decision.consensus_strength:.0%}")
    print(f"   Voting Method: {decision.voting_method.value}\n")
    
    print("📊 Individual Votes:")
    for member, vote in decision.individual_votes.items():
        print(f"   • {member}: {vote}")
    
    if decision.conflicts:
        print(f"\n⚠️  Predicted Conflicts: {len(decision.conflicts)}")
        for conflict in decision.conflicts:
            print(f"   • {' vs '.join(conflict.between)}")
            print(f"     Reason: {conflict.reason}")
            print(f"     Severity: {conflict.severity:.0%}")
    else:
        print("\n✓ No conflicts predicted - team is aligned!")
    
    print()


def example_2_voting_methods():
    """Example 2: Compare different voting methods."""
    print("\n═══ Example 2: Voting Method Comparison ═══\n")
    
    # Create diverse team
    members = [
        quick_twin(openness=0.9, name="Innovator"),
        quick_twin(openness=0.3, name="Traditionalist"),
        quick_twin(openness=0.6, name="Moderate1"),
        quick_twin(openness=0.5, name="Moderate2"),
    ]
    
    team = create_team_twin(members, name="Strategy Team")
    
    question = "Pivot product to new market segment?"
    context = {"risk": "high", "potential": "large"}
    
    print(f"Question: {question}\n")
    
    # Test different voting methods
    for method in ["majority", "consensus", "unanimous"]:
        decision = team.simulate_team_decision(
            question,
            context,
            voting_method=method
        )
        
        print(f"🗳️  {method.upper()}:")
        print(f"   Result: {decision.outcome}")
        print(f"   Consensus: {decision.consensus_strength:.0%}")
        print()


def example_3_conflict_prediction():
    """Example 3: Predict team conflicts."""
    print("\n═══ Example 3: Conflict Prediction ═══\n")
    
    # Create team with opposing personalities
    risk_taker = quick_twin(
        openness=0.9,
        neuroticism=0.2,
        name="Risk Taker"
    )
    
    risk_averse = quick_twin(
        openness=0.2,
        neuroticism=0.9,
        name="Risk Averse"
    )
    
    mediator = quick_twin(
        openness=0.5,
        agreeableness=0.9,
        name="Mediator"
    )
    
    team = create_team_twin(
        [risk_taker, risk_averse, mediator],
        name="Leadership Team"
    )
    
    print(f"Created: {team}\n")
    
    # Predict conflicts for a scenario
    conflicts = team.predict_conflicts(
        "Restructure company into new organizational model",
        context={"timeline": "immediate", "impact": "significant"}
    )
    
    print(f"⚠️  Predicted Conflicts: {len(conflicts)}\n")
    
    for i, conflict in enumerate(conflicts, 1):
        print(f"{i}. {' vs '.join(conflict.between)}")
        print(f"   Reason: {conflict.reason}")
        print(f"   Severity: {conflict.severity:.0%}")
        print(f"   Key Differences:")
        for trait, diff in conflict.trait_differences.items():
            if diff > 0.4:  # Only show significant differences
                print(f"     - {trait.title()}: {diff:.2f} difference")
        print()


def example_4_team_composition():
    """Example 4: Analyze team composition."""
    print("\n═══ Example 4: Team Composition Analysis ═══\n")
    
    # Create team
    team = create_team_twin([
        quick_twin(openness=0.8, conscientiousness=0.7, extraversion=0.6, name="Member 1"),
        quick_twin(openness=0.6, conscientiousness=0.8, extraversion=0.4, name="Member 2"),
        quick_twin(openness=0.7, conscientiousness=0.6, extraversion=0.7, name="Member 3"),
    ], name="Engineering Team")
    
    # Get composition analysis
    composition = team.get_team_composition()
    
    print(f"📊 Team: {team.name}\n")
    print(f"Size: {composition['size']} members")
    print(f"Diversity Score: {composition['diversity_score']:.2f}\n")
    
    print("Average Personality Traits:")
    for trait, value in composition['avg_traits'].items():
        bar = "█" * int(value * 20)
        print(f"  {trait.title():20s} [{bar:<20s}] {value:.2f}")
    
    print()
    
    if composition['high_traits']:
        print(f"✓ Team strengths: {', '.join(composition['high_traits'])}")
    
    if composition['low_traits']:
        print(f"⚠ Team gaps: {', '.join(composition['low_traits'])}")
    
    print()


def example_5_collaboration_optimization():
    """Example 5: Get collaboration recommendations."""
    print("\n═══ Example 5: Collaboration Optimization ═══\n")
    
    # Create team with potential issues
    team = create_team_twin([
        quick_twin(
            openness=0.4,
            agreeableness=0.3,  # Low agreeableness
            neuroticism=0.8,     # High stress
            name="Stressed Dev"
        ),
        quick_twin(
            openness=0.5,
            agreeableness=0.4,  # Low agreeableness
            neuroticism=0.7,     # High stress
            name="Anxious PM"
        ),
        quick_twin(
            openness=0.3,
            agreeableness=0.3,  # Low agreeableness
            neuroticism=0.9,     # Very high stress
            name="Worried Designer"
        ),
    ], name="Stressed Team")
    
    print(f"Analyzing: {team.name}\n")
    
    # Get recommendations
    analysis = team.optimize_collaboration()
    
    print("📋 Recommendations:\n")
    for i, rec in enumerate(analysis['recommendations'], 1):
        print(f"{i}. {rec}")
    
    print()


def example_6_real_world_scenario():
    """Example 6: Real-world product decision."""
    print("\n═══ Example 6: Real Product Decision ═══\n")
    
    # Create realistic product team
    pm = quick_twin(
        openness=0.7,
        conscientiousness=0.8,
        extraversion=0.7,
        name="Product Manager"
    )
    
    eng_lead = quick_twin(
        openness=0.6,
        conscientiousness=0.9,
        extraversion=0.4,
        name="Engineering Lead"
    )
    
    designer = quick_twin(
        openness=0.9,
        conscientiousness=0.6,
        extraversion=0.6,
        name="Designer"
    )
    
    finance = quick_twin(
        openness=0.4,
        conscientiousness=0.9,
        extraversion=0.5,
        name="Finance Lead"
    )
    
    team = create_team_twin(
        [pm, eng_lead, designer, finance],
        name="Product Launch Team"
    )
    
    print(f"Team: {team.name}\n")
    
    # Real decision scenario
    decision = team.simulate_team_decision(
        "Launch beta version next month vs wait for full polish (3 months)?",
        context={
            "current_readiness": "70%",
            "competitor_status": "planning launch in 2 months",
            "user_demand": "high",
            "technical_debt": "moderate",
            "revenue_at_stake": "$500K"
        },
        voting_method="weighted"  # Weight by confidence
    )
    
    print("🎯 Decision:")
    print(f"   {decision.outcome}\n")
    
    print("📊 How team voted:")
    for member, vote in decision.individual_votes.items():
        print(f"   {member:20s} → {vote}")
    
    print(f"\n💪 Consensus Strength: {decision.consensus_strength:.0%}")
    print(f"📝 Reasoning: {decision.reasoning}\n")
    
    if decision.conflicts:
        print(f"⚠️  Areas of disagreement:")
        for conflict in decision.conflicts[:2]:  # Show top 2
            print(f"   • {conflict.reason}")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("TEAM DIGITAL TWIN - GROUP SIMULATION EXAMPLES")
    print("="*70 + "\n")
    
    # Configure (using default provider)
    use_openai()
    
    try:
        example_1_simple_team_decision()
        print("-"*70)
        
        example_2_voting_methods()
        print("-"*70)
        
        example_3_conflict_prediction()
        print("-"*70)
        
        example_4_team_composition()
        print("-"*70)
        
        example_5_collaboration_optimization()
        print("-"*70)
        
        example_6_real_world_scenario()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("  1. Set OPENAI_API_KEY or GEMINI_API_KEY")
        print("  2. Installed: pip install openai  (or google-generativeai)")
    
    print("\n" + "="*70)
    print("✓ Examples complete!")
    print("="*70 + "\n")
    
    print("💡 Team Digital Twins enable:")
    print("   • Simulate group decisions before meetings")
    print("   • Predict conflicts early")
    print("   • Optimize team composition")
    print("   • Test different decision-making approaches")
    print("\n💡 Try building your own team twin:")
    print("   from simulacrum import create_team_twin")
    print("   team = create_team_twin([member1, member2, member3])")
    print("   decision = team.simulate_team_decision('Question?')")
    print()


if __name__ == "__main__":
    main()
