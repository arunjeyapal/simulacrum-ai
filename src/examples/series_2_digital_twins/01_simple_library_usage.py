# examples/series_2_digital_twins/01_simple_library_usage.py
"""
Digital Twin Library - Simple Usage Example

This demonstrates how easy it is to use simulacrum-ai as a library
in your own projects.

Run:
    python 01_simple_library_usage.py
"""

# IMPORTANT: This is how users will import the library
# No complicated setup - just import and use!

from simulacrum import DigitalTwin, create_twin_from_survey, quick_twin


def example_1_quick_twin():
    """Example 1: Create a quick twin for testing."""
    print("═══ Example 1: Quick Twin Creation ═══\n")
    
    # Create a twin with specific traits
    twin = quick_twin(
        openness=0.85,          # Innovative
        conscientiousness=0.70,  # Organized
        extraversion=0.45,       # Moderate
        agreeableness=0.60,      # Cooperative
        neuroticism=0.30,        # Calm
        name="Alice"
    )
    
    print(f"Created: {twin}")
    print(f"Traits: {twin.traits}")
    
    # Simulate a decision
    decision = twin.simulate_decision(
        "Should I take a risky new job at a startup?",
        context={
            "salary": 120000,
            "equity": "0.5%",
            "risk_level": "high",
            "learning_opportunity": "excellent"
        }
    )
    
    print(f"\nDecision: {decision.recommendation}")
    print(f"Reasoning: {decision.reasoning}")
    print(f"Confidence: {decision.confidence:.0%}")
    print()


def example_2_from_survey():
    """Example 2: Create twin from survey responses."""
    print("═══ Example 2: From Survey Responses ═══\n")
    
    # Simulate survey responses (in real usage, these come from user)
    survey_responses = {
        "openness_1": 5,     # I enjoy trying new things
        "openness_2": 4,     # I am interested in many topics
        "openness_3": 5,     # I love learning
        # ... in production, 50 questions
        # This is simplified for demo
    }
    
    # Create twin from survey
    twin = create_twin_from_survey(
        survey_responses,
        name="Bob"
    )
    
    print(f"Created: {twin}")
    print(f"Calibration Score: {twin.get_calibration_score():.1%}")
    
    # Simulate multiple decisions
    questions = [
        "Invest in cryptocurrency?",
        "Start a side business?",
        "Go back to school for MBA?"
    ]
    
    for question in questions:
        decision = twin.simulate_decision(question)
        print(f"\n{question}")
        print(f"  → {decision.recommendation} ({decision.confidence:.0%} confident)")


def example_3_integration_in_your_code():
    """Example 3: How you'd integrate this in your own code."""
    print("\n═══ Example 3: Integration in Your Code ═══\n")
    
    # Imagine this is your application's decision support system
    
    def career_decision_support(user_profile, job_offers):
        """Help user decide between job offers using their digital twin."""
        
        # Create user's digital twin
        twin = DigitalTwin.from_survey(
            user_profile["survey_responses"],
            name=user_profile["name"]
        )
        
        # Evaluate each offer
        results = []
        for offer in job_offers:
            decision = twin.simulate_decision(
                f"Accept {offer['company']} offer?",
                context=offer
            )
            results.append({
                "company": offer["company"],
                "recommendation": decision.recommendation,
                "confidence": decision.confidence,
                "reasoning": decision.reasoning
            })
        
        return results
    
    # Your application code
    user = {
        "name": "Alice",
        "survey_responses": {"openness_1": 5, "openness_2": 4}  # Simplified
    }
    
    job_offers = [
        {"company": "BigCorp", "salary": 150000, "role": "Senior PM", "risk": "low"},
        {"company": "Startup", "salary": 110000, "role": "VP Product", "risk": "high"}
    ]
    
    # Get AI-powered recommendations
    recommendations = career_decision_support(user, job_offers)
    
    print("Career Recommendations:")
    for rec in recommendations:
        print(f"\n{rec['company']}:")
        print(f"  {rec['recommendation']} ({rec['confidence']:.0%} confident)")
        print(f"  Why: {rec['reasoning']}")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("SIMULACRUM DIGITAL TWIN LIBRARY - USAGE EXAMPLES")
    print("="*60 + "\n")
    
    print("This shows how easy it is to use simulacrum-ai in your projects.")
    print("Just: pip install simulacrum-ai\n")
    
    example_1_quick_twin()
    print("\n" + "-"*60 + "\n")
    
    example_2_from_survey()
    print("\n" + "-"*60 + "\n")
    
    example_3_integration_in_your_code()
    
    print("\n" + "="*60)
    print("✓ Complete! Now integrate into YOUR projects.")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
