# src/simulacrum/core/llm.py (COMPLETE REWRITE - Multi-Provider)
from __future__ import annotations
"""
Multi-provider LLM integration for personality-driven decision simulation.

Supports:
- OpenAI (GPT-4, GPT-4-turbo, GPT-3.5-turbo)
- Google Gemini (gemini-pro, gemini-1.5-pro)
- Anthropic Claude (optional)
"""

import os
from typing import TYPE_CHECKING, Dict, Any, Optional, Literal
from dataclasses import dataclass
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from ..agents.persona import PsychologicalProfile


# Provider type
ProviderType = Literal["openai", "gemini", "anthropic"]


@dataclass
class LLMConfig:
    """
    Configuration for LLM integration.
    
    Attributes:
        provider: LLM provider ("openai", "gemini", or "anthropic")
        model: Model name
        api_key: API key (or None to use environment variable)
        max_tokens: Max tokens per generation
        temperature: Temperature for generation (0.0-1.0)
    """
    provider: ProviderType = "openai"
    model: str = "gpt-4-turbo"
    api_key: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.7
    
    def __post_init__(self):
        """Load API key from environment if not provided."""
        if self.api_key is None:
            # Try to load from environment based on provider
            if self.provider == "openai":
                self.api_key = os.getenv("OPENAI_API_KEY")
                if not self.api_key:
                    raise ValueError(
                        "OPENAI_API_KEY not found. Either:\n"
                        "  1. Set environment variable: export OPENAI_API_KEY='your-key'\n"
                        "  2. Pass api_key to configure(): configure(api_key='your-key')"
                    )
            elif self.provider == "gemini":
                self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
                if not self.api_key:
                    raise ValueError(
                        "GEMINI_API_KEY not found. Either:\n"
                        "  1. Set environment variable: export GEMINI_API_KEY='your-key'\n"
                        "  2. Pass api_key to configure(): configure(api_key='your-key')"
                    )
            elif self.provider == "anthropic":
                self.api_key = os.getenv("ANTHROPIC_API_KEY")
                if not self.api_key:
                    raise ValueError(
                        "ANTHROPIC_API_KEY not found. Either:\n"
                        "  1. Set environment variable: export ANTHROPIC_API_KEY='your-key'\n"
                        "  2. Pass api_key to configure(): configure(api_key='your-key')"
                    )


class BaseLLMProvider(ABC):
    """Base class for LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str, config: LLMConfig) -> str:
        """Generate response from LLM."""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider."""
    
    def __init__(self):
        """Initialize OpenAI provider."""
        try:
            import openai
            self.openai = openai
        except ImportError:
            raise ImportError(
                "OpenAI package not installed. Install with:\n"
                "  pip install openai"
            )
    
    def generate(self, prompt: str, config: LLMConfig) -> str:
        """Generate response using OpenAI API."""
        client = self.openai.OpenAI(api_key=config.api_key)
        
        response = client.chat.completions.create(
            model=config.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=config.max_tokens,
            temperature=config.temperature
        )
        
        return response.choices[0].message.content


class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider."""
    
    def __init__(self):
        """Initialize Gemini provider."""
        try:
            import google.generativeai as genai
            self.genai = genai
        except ImportError:
            raise ImportError(
                "Google Generative AI package not installed. Install with:\n"
                "  pip install google-generativeai"
            )
    
    def generate(self, prompt: str, config: LLMConfig) -> str:
        """Generate response using Gemini API."""
        self.genai.configure(api_key=config.api_key)
        
        model = self.genai.GenerativeModel(config.model)
        
        generation_config = self.genai.types.GenerationConfig(
            max_output_tokens=config.max_tokens,
            temperature=config.temperature
        )
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        return response.text


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider (optional)."""
    
    def __init__(self):
        """Initialize Anthropic provider."""
        try:
            import anthropic
            self.anthropic = anthropic
        except ImportError:
            raise ImportError(
                "Anthropic package not installed. Install with:\n"
                "  pip install anthropic"
            )
    
    def generate(self, prompt: str, config: LLMConfig) -> str:
        """Generate response using Anthropic API."""
        client = self.anthropic.Anthropic(api_key=config.api_key)
        
        response = client.messages.create(
            model=config.model,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text


def get_provider(provider_type: ProviderType) -> BaseLLMProvider:
    """
    Get LLM provider instance.
    
    Args:
        provider_type: "openai", "gemini", or "anthropic"
        
    Returns:
        Provider instance
    """
    if provider_type == "openai":
        return OpenAIProvider()
    elif provider_type == "gemini":
        return GeminiProvider()
    elif provider_type == "anthropic":
        return AnthropicProvider()
    else:
        raise ValueError(f"Unknown provider: {provider_type}")


class PersonalityLLM:
    """
    Multi-provider LLM interface for personality-driven decision simulation.
    
    Supports OpenAI (GPT), Google (Gemini), and Anthropic (Claude).
    
    Examples:
        >>> # Using OpenAI (default)
        >>> llm = PersonalityLLM()
        >>> 
        >>> # Using Gemini
        >>> config = LLMConfig(provider="gemini", model="gemini-1.5-pro")
        >>> llm = PersonalityLLM(config)
        >>> 
        >>> # Generate decision
        >>> decision = llm.generate_decision(
        ...     personality=traits,
        ...     question="Should I take this risky job?",
        ...     context={"salary": 120000}
        ... )
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize LLM interface.
        
        Args:
            config: Optional LLM configuration. If None, uses OpenAI with gpt-4-turbo.
        """
        self.config = config or LLMConfig()
        self.provider = get_provider(self.config.provider)
    
    def generate_decision(
        self,
        personality: PsychologicalProfile,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        name: str = "this person",
        past_experiences: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Generate a personality-driven decision.
        
        Args:
            personality: Big Five personality traits
            question: The decision to make
            context: Additional context for the decision
            name: Person's name (for personalization)
            past_experiences: Optional relevant memories
            
        Returns:
            Dictionary with:
                - recommendation: "Accept" or "Decline" or custom
                - reasoning: Natural language explanation
                - confidence: 0.0-1.0 score
                - alternatives_considered: List of alternatives
                - personality_factors: Which traits influenced decision
                
        Examples:
            >>> decision = llm.generate_decision(
            ...     personality=traits,
            ...     question="Accept startup job offer?",
            ...     context={"salary": 100000, "equity": "0.5%"}
            ... )
        """
        # Build personality-infused prompt
        prompt = self._build_decision_prompt(
            personality=personality,
            question=question,
            context=context or {},
            name=name,
            past_experiences=past_experiences or []
        )
        
        # Call LLM
        try:
            response_text = self.provider.generate(prompt, self.config)
            
            # Parse response
            decision = self._parse_decision_response(
                response_text,
                personality
            )
            
            return decision
            
        except Exception as e:
            raise RuntimeError(f"LLM API error: {e}")
    
    def _build_decision_prompt(
        self,
        personality: PsychologicalProfile,
        question: str,
        context: Dict[str, Any],
        name: str,
        past_experiences: list
    ) -> str:
        """Build personality-infused prompt for decision simulation."""
        
        # Personality description
        personality_desc = self._describe_personality(personality)
        
        # Context formatting
        context_str = self._format_context(context)
        
        # Past experiences
        experiences_str = ""
        if past_experiences:
            exp_items = "\n".join([f"- {exp.get('description', exp)}" 
                                   for exp in past_experiences[:5]])
            experiences_str = f"\n\nRelevant past experiences:\n{exp_items}"
        
        # Build complete prompt
        prompt = f"""You are simulating how {name} would make a decision.

PERSONALITY PROFILE:
{personality_desc}

DECISION TO MAKE:
{question}

CONTEXT:
{context_str}{experiences_str}

Based on this personality, how would {name} decide?

Respond in this exact format:

DECISION: [Accept/Decline/other specific choice]
REASONING: [2-3 sentences explaining why this personality would make this choice]
CONFIDENCE: [0-100]
ALTERNATIVES: [Brief list of other options considered]
KEY TRAITS: [Which personality traits most influenced this decision]

Remember: You are simulating this specific person's decision-making, not giving general advice.
The decision should reflect their personality traits, especially their dominant characteristics."""

        return prompt
    
    def _describe_personality(self, traits: PsychologicalProfile) -> str:
        """Create natural language description of personality."""
        descriptions = []
        
        # Openness
        if traits.openness > 0.7:
            descriptions.append("• Highly open to new experiences, creative, and imaginative")
        elif traits.openness < 0.4:
            descriptions.append("• Prefers familiar approaches, practical, conventional")
        else:
            descriptions.append("• Moderately open to new experiences")
        
        # Conscientiousness
        if traits.conscientiousness > 0.7:
            descriptions.append("• Very organized, disciplined, and detail-oriented")
        elif traits.conscientiousness < 0.4:
            descriptions.append("• Spontaneous, flexible, less focused on planning")
        else:
            descriptions.append("• Moderately organized and planful")
        
        # Extraversion
        if traits.extraversion > 0.7:
            descriptions.append("• Highly extraverted, energized by social interaction")
        elif traits.extraversion < 0.4:
            descriptions.append("• Introverted, prefers solitude, reserved")
        else:
            descriptions.append("• Balanced between introversion and extraversion")
        
        # Agreeableness
        if traits.agreeableness > 0.7:
            descriptions.append("• Very cooperative, empathetic, and considerate")
        elif traits.agreeableness < 0.4:
            descriptions.append("• Direct, competitive, skeptical")
        else:
            descriptions.append("• Moderately cooperative and considerate")
        
        # Neuroticism
        if traits.neuroticism > 0.7:
            descriptions.append("• Prone to anxiety, stress-sensitive, cautious")
        elif traits.neuroticism < 0.4:
            descriptions.append("• Emotionally stable, calm, resilient")
        else:
            descriptions.append("• Moderately emotionally stable")
        
        # Numerical traits
        trait_values = f"""
Trait scores (0.0 = low, 1.0 = high):
- Openness: {traits.openness:.2f}
- Conscientiousness: {traits.conscientiousness:.2f}
- Extraversion: {traits.extraversion:.2f}
- Agreeableness: {traits.agreeableness:.2f}
- Neuroticism: {traits.neuroticism:.2f}
"""
        
        return "\n".join(descriptions) + "\n" + trait_values
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dictionary into readable text."""
        if not context:
            return "No additional context provided."
        
        items = []
        for key, value in context.items():
            formatted_key = key.replace("_", " ").title()
            items.append(f"- {formatted_key}: {value}")
        
        return "\n".join(items)
    
    def _parse_decision_response(
        self,
        response_text: str,
        personality: PsychologicalProfile
    ) -> Dict[str, Any]:
        """Parse LLM response into structured decision."""
        
        decision = {
            "recommendation": "Unknown",
            "reasoning": "",
            "confidence": 0.5,
            "alternatives_considered": [],
            "personality_factors": {}
        }
        
        lines = response_text.strip().split("\n")
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith("DECISION:"):
                decision["recommendation"] = line.split(":", 1)[1].strip()
                
            elif line.startswith("REASONING:"):
                reasoning = line.split(":", 1)[1].strip()
                current_section = "reasoning"
                decision["reasoning"] = reasoning
                
            elif line.startswith("CONFIDENCE:"):
                try:
                    conf_str = line.split(":", 1)[1].strip()
                    conf_num = float(''.join(c for c in conf_str if c.isdigit() or c == '.'))
                    if conf_num > 1:
                        conf_num = conf_num / 100
                    decision["confidence"] = max(0.0, min(1.0, conf_num))
                except:
                    decision["confidence"] = 0.5
                current_section = None
                
            elif line.startswith("ALTERNATIVES:"):
                alts = line.split(":", 1)[1].strip()
                decision["alternatives_considered"] = [a.strip() for a in alts.split(",")]
                current_section = None
                
            elif line.startswith("KEY TRAITS:"):
                traits_str = line.split(":", 1)[1].strip().lower()
                if "openness" in traits_str:
                    decision["personality_factors"]["openness"] = personality.openness
                if "conscientiousness" in traits_str:
                    decision["personality_factors"]["conscientiousness"] = personality.conscientiousness
                if "extraversion" in traits_str:
                    decision["personality_factors"]["extraversion"] = personality.extraversion
                if "agreeableness" in traits_str:
                    decision["personality_factors"]["agreeableness"] = personality.agreeableness
                if "neuroticism" in traits_str:
                    decision["personality_factors"]["neuroticism"] = personality.neuroticism
                current_section = None
                
            elif current_section == "reasoning" and line and not line.startswith(("DECISION:", "CONFIDENCE:", "ALTERNATIVES:", "KEY TRAITS:")):
                decision["reasoning"] += " " + line
        
        decision["reasoning"] = decision["reasoning"].strip()
        
        if not decision["personality_factors"]:
            decision["personality_factors"] = self._identify_dominant_traits(personality)
        
        return decision
    
    def _identify_dominant_traits(self, personality: PsychologicalProfile) -> Dict[str, float]:
        """Identify which traits are most dominant."""
        traits = {
            "openness": personality.openness,
            "conscientiousness": personality.conscientiousness,
            "extraversion": personality.extraversion,
            "agreeableness": personality.agreeableness,
            "neuroticism": personality.neuroticism
        }
        
        dominant = {}
        for trait, value in traits.items():
            if value > 0.6 or value < 0.4:
                dominant[trait] = value
        
        if not dominant:
            sorted_traits = sorted(traits.items(), key=lambda x: abs(x[1] - 0.5), reverse=True)
            dominant = dict(sorted_traits[:2])
        
        return dominant


# Global LLM instance
_llm_instance: Optional[PersonalityLLM] = None

def get_llm(config: Optional[LLMConfig] = None) -> PersonalityLLM:
    """
    Get or create global LLM instance.
    
    Args:
        config: Optional configuration. If None, uses existing or creates default.
        
    Returns:
        PersonalityLLM instance
        
    Examples:
        >>> from simulacrum.core.llm import get_llm, LLMConfig
        >>> 
        >>> # Using OpenAI (default)
        >>> llm = get_llm()
        >>> 
        >>> # Using Gemini
        >>> config = LLMConfig(provider="gemini", model="gemini-1.5-pro")
        >>> llm = get_llm(config)
    """
    global _llm_instance
    
    if _llm_instance is None or config is not None:
        _llm_instance = PersonalityLLM(config)
    
    return _llm_instance
