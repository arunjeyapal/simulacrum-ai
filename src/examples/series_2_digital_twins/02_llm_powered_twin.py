# examples/series_2_digital_twins/02_llm_powered_twin.py (UPDATED)
"""
LLM-Powered Digital Twin Example - Multi-Provider Support

Demonstrates using OpenAI (GPT), Google (Gemini), or Anthropic (Claude)
for personality-driven AI decisions.

Prerequisites:
    # For OpenAI (recommended):
    export OPENAI_API_KEY="sk-..."
    pip install openai
    
    # For Gemini:
    export GEMINI_API_KEY="..."
    pip install google-generativeai
    
    # For Anthropic (optional):
    export ANTHROPIC_API_KEY="sk-ant-..."
    pip install anthropic

Run:
    python 02_llm_powered_twin.py
"""

import os
from simulacrum import (
    DigitalTwin,
    configure,
    use_openai,
    use_gemini,
    quick_twin,
    print_config
)


def check_available_providers():
    """Check which API keys are available."""
    providers = []
    
    if os.getenv("OPENAI_API_KEY"):
        providers.append("openai")
    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        providers.append("gemini")
    if os.getenv("ANTHROPIC_API_KEY"):
        providers.append("anthropic")
    
    return providers


def show_provider_setup():
    """Show setup instructions for providers."""
    print("="*70)
    print("PROVIDER SETUP")
    print("="*70)
    print("\nYou can use any of these AI providers:\n")
    
    print("1️⃣  OpenAI (GPT) - Recommended")
    print("   export OPENAI_API_KEY='sk-...'")
    print("   pip install openai")
    print()
    
    print("2️⃣  Google Gemini")
    print("   export GEMINI_API_KEY='...'")
    print("   pip install google-generativeai")
    print()
    
    print("3️⃣  Anthropic Claude (optional)")
    print("   export ANTHROPIC_API_KEY='sk-ant-...'")
    print("   pip install anthropic")
    print()
    
    available = check_available_providers()
    if available:
        print(f"✓ Available providers: {', '.join(available).upper()}")
    else:
        print("⚠️  No API keys found. Set one of the above environment variables.")
    
    print("="*70 + "\n")
    
    return available


def example_1_openai():
    """Example 1: Using OpenAI GPT."""
    print("═══ Example 1: OpenAI (GPT-4) ═══\n")
    
    # Configure for OpenAI
    use_openai()  # Uses OPENAI_API_KEY from environment
    
    # Or explicitly:
    # use_openai(api_key="sk-...", model="gpt-4-turbo")
    
    print("✓ Configured for OpenAI GPT-4-turbo\n")
    
    # Create twin
    twin = quick_twin(
        openness=0.85,
        conscientiousness=0.70,
        neuroticism=0.30,
        name="GPT Twin"
    )
    
    # Make decision
    decision = twin.simulate_decision(
        "Should I leave my stable job to join an AI startup?",
        context={
            "current_salary": 150000,
            "startup_salary": 120000,
            "startup_equity": "1.5%",
            "risk_level": "high"
        }
    )
    
    print(f"🤖 {twin.name} Decision:")
    print(f"   → {decision.recommendation} ({decision.confidence:.0%} confident)")
    print(f"   Why: {decision.reasoning}\n")


def example_2_gemini():
    """Example 2: Using Google Gemini."""
    print("\n═══ Example 2: Google Gemini ═══\n")
    
    # Configure for Gemini
    use_gemini()  # Uses GEMINI_API_KEY from environment
    
    # Or explicitly:
    # use_gemini(api_key="...", model="gemini-1.5-pro")
    
    print("✓ Configured for Google Gemini 1.5 Pro\n")
    
    # Create twin
    twin = quick_twin(
        openness=0.35,
        neuroticism=0.75,
        name="Gemini Twin"
    )
    
    # Make decision
    decision = twin.simulate_decision(
        "Invest $10,000 in cryptocurrency?",
        context={
            "amount": 10000,
            "asset": "Bitcoin",
            "volatility": "high",
            "potential_return": "50-200%"
        }
    )
    
    print(f"🤖 {twin.name} Decision:")
    print(f"   → {decision.recommendation} ({decision.confidence:.0%} confident)")
    print(f"   Why: {decision.reasoning}\n")


def example_3_comparison():
    """Example 3: Compare same twin across different providers."""
    print("\n═══ Example 3: Multi-Provider Comparison ═══\n")
    
    available = check_available_providers()
    
    if len(available) < 2:
        print("⚠️  Need at least 2 providers to compare.")
        print("   Set multiple API keys to see differences.\n")
        return
    
    # Same personality
    traits = {
        "openness": 0.8,
        "conscientiousness": 0.6,
        "extraversion": 0.5,
        "agreeableness": 0.6,
        "neuroticism": 0.4
    }
    
    question = "Accept challenging lead role on uncertain project?"
    context = {
        "role": "Technical Lead",
        "project_status": "behind schedule",
        "team_morale": "low",
        "opportunity": "high visibility"
    }
    
    results = {}
    
    # Test each available provider
    for provider in available[:2]:  # Test first 2
        if provider == "openai":
            use_openai()
            twin = quick_twin(**traits, name="OpenAI Twin")
        elif provider == "gemini":
            use_gemini()
            twin = quick_twin(**traits, name="Gemini Twin")
        
        decision = twin.simulate_decision(question, context)
        results[provider] = decision
    
    # Show comparison
    print(f"Question: {question}\n")
    print("Same personality, different AI providers:\n")
    
    for provider, decision in results.items():
        print(f"🤖 {provider.upper()}:")
        print(f"   → {decision.recommendation} ({decision.confidence:.0%} confident)")
        print(f"   Why: {decision.reasoning}\n")


def example_4_switch_providers():
    """Example 4: Switching providers dynamically."""
    print("\n═══ Example 4: Dynamic Provider Switching ═══\n")
    
    available = check_available_providers()
    
    if not available:
        print("⚠️  No providers available.")
        return
    
    twin = quick_twin(openness=0.7, name="Flexible Twin")
    
    # Use first available provider
    primary = available[0]
    
    if primary == "openai":
        use_openai()
    elif primary == "gemini":
        use_gemini()
    
    print(f"✓ Using {primary.upper()}\n")
    
    decision1 = twin.simulate_decision("Take unpaid leave to travel?")
    print(f"Decision 1: {decision1.recommendation}")
    
    # Switch provider if another available
    if len(available) > 1:
        secondary = available[1]
        
        if secondary == "openai":
            use_openai()
        elif secondary == "gemini":
            use_gemini()
        
        print(f"\n✓ Switched to {secondary.upper()}\n")
        
        decision2 = twin.simulate_decision("Start side business?")
        print(f"Decision 2: {decision2.recommendation}")
    
    print()


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("LLM-POWERED DIGITAL TWINS - MULTI-PROVIDER SUPPORT")
    print("="*70 + "\n")
    
    # Show provider setup
    available = show_provider_setup()
    
    if not available:
        print("\n❌ No API keys found!")
        print("\nTo use this example:")
        print("  1. Get an API key from OpenAI or Google")
        print("  2. Set environment variable:")
        print("     export OPENAI_API_KEY='sk-...'  # or")
        print("     export GEMINI_API_KEY='...'")
        print("  3. Install the package:")
        print("     pip install openai  # or")
        print("     pip install google-generativeai")
        return
    
    # Show current config
    print_config()
    print()
    
    try:
        # Run examples based on available providers
        if "openai" in available:
            example_1_openai()
            print("-"*70)
        
        if "gemini" in available:
            example_2_gemini()
            print("-"*70)
        
        if len(available) >= 2:
            example_3_comparison()
            print("-"*70)
        
        example_4_switch_providers()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nIf this is an API error:")
        print("  - Check your API key is correct")
        print("  - Ensure you have API credits")
        print("  - Verify the package is installed:")
        print("    pip install openai  # or google-generativeai")
    
    print("\n" + "="*70)
    print("✓ Examples complete!")
    print("="*70 + "\n")
    
    print("💡 Provider flexibility:")
    print("   - Use OpenAI for best results (GPT-4)")
    print("   - Use Gemini for Google ecosystem")
    print("   - Switch providers anytime with configure()")
    print("\n💡 Your digital twins work with ANY provider!")
    print()


if __name__ == "__main__":
    main()
