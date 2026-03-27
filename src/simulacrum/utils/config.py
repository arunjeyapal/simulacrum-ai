# src/simulacrum/utils/config.py (UPDATED - Multi-Provider Support)
"""
Configuration system for simulacrum-ai library.

Supports OpenAI (GPT), Google (Gemini), and Anthropic (Claude).
"""

import os
from typing import Optional, Dict, Any, Literal
from dataclasses import dataclass, field

try:
    from dotenv import load_dotenv
    load_dotenv(override=False)  # don't override already-exported vars
except ImportError:
    pass


ProviderType = Literal["openai", "gemini", "anthropic"]


@dataclass
class SimulacrumConfig:
    """
    Global configuration for simulacrum-ai.
    
    Attributes:
        llm_provider: LLM provider ("openai", "gemini", or "anthropic")
        llm_model: Model name
        llm_api_key: API key (or None to use environment variable)
        llm_temperature: Temperature for generation
        llm_max_tokens: Max tokens per generation
        cache_enabled: Whether to cache LLM responses
        log_level: Logging level
        debug_mode: Enable debug output
    """
    # LLM settings
    llm_provider: ProviderType = "openai"
    llm_model: str = "gpt-4-turbo"
    llm_api_key: Optional[str] = None
    llm_temperature: float = 0.7
    llm_max_tokens: int = 1000
    
    # System settings
    cache_enabled: bool = False
    log_level: str = "INFO"
    debug_mode: bool = False
    
    # Additional settings
    extra: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Load settings from environment variables if not provided."""
        # API key from environment based on provider
        if self.llm_api_key is None:
            if self.llm_provider == "openai":
                self.llm_api_key = os.getenv("OPENAI_API_KEY")
            elif self.llm_provider == "gemini":
                self.llm_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            elif self.llm_provider == "anthropic":
                self.llm_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Log level from environment
        env_log_level = os.getenv("SIMULACRUM_LOG_LEVEL")
        if env_log_level:
            self.log_level = env_log_level.upper()
        
        # Debug mode from environment
        env_debug = os.getenv("SIMULACRUM_DEBUG", "").lower()
        if env_debug in ("1", "true", "yes"):
            self.debug_mode = True


# Global configuration instance
_config: Optional[SimulacrumConfig] = None


def configure(
    provider: ProviderType = "openai",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1000,
    cache_enabled: bool = False,
    log_level: str = "INFO",
    debug: bool = False,
    **kwargs
) -> SimulacrumConfig:
    """
    Configure simulacrum-ai library settings.
    
    Args:
        provider: LLM provider ("openai", "gemini", or "anthropic")
        model: Model name (auto-selects default if None)
        api_key: API key (or use environment variable)
        temperature: LLM temperature (0.0-1.0)
        max_tokens: Max tokens per generation
        cache_enabled: Enable response caching
        log_level: Logging level ("DEBUG", "INFO", "WARNING", "ERROR")
        debug: Enable debug mode
        **kwargs: Additional settings
        
    Returns:
        SimulacrumConfig instance
        
    Examples:
        >>> from simulacrum import configure
        >>> 
        >>> # Using OpenAI (default)
        >>> configure(
        ...     provider="openai",
        ...     model="gpt-4-turbo",
        ...     api_key="sk-..."  # or use OPENAI_API_KEY env var
        ... )
        >>> 
        >>> # Using Gemini
        >>> configure(
        ...     provider="gemini",
        ...     model="gemini-1.5-pro",
        ...     api_key="..."  # or use GEMINI_API_KEY env var
        ... )
        >>> 
        >>> # Using environment variables:
        >>> # export OPENAI_API_KEY="sk-..."
        >>> configure()  # Auto-detects OpenAI
    """
    global _config
    
    # Auto-select model based on provider if not specified
    if model is None:
        if provider == "openai":
            model = "gpt-4-turbo"
        elif provider == "gemini":
            model = "gemini-1.5-pro"
        elif provider == "anthropic":
            model = "claude-sonnet-4-20250514"
    
    _config = SimulacrumConfig(
        llm_provider=provider,
        llm_model=model,
        llm_api_key=api_key,
        llm_temperature=temperature,
        llm_max_tokens=max_tokens,
        cache_enabled=cache_enabled,
        log_level=log_level,
        debug_mode=debug,
        extra=kwargs
    )
    
    # Apply configuration to LLM
    from ..core.llm import get_llm, LLMConfig
    
    llm_config = LLMConfig(
        provider=_config.llm_provider,
        model=_config.llm_model,
        api_key=_config.llm_api_key,
        max_tokens=_config.llm_max_tokens,
        temperature=_config.llm_temperature
    )
    
    # Initialize LLM with config
    get_llm(llm_config)
    
    return _config


def get_config() -> SimulacrumConfig:
    """
    Get current configuration.
    
    Returns:
        SimulacrumConfig instance (creates default if not configured)
    """
    global _config
    
    if _config is None:
        _config = SimulacrumConfig()
    
    return _config


def reset_config() -> None:
    """Reset configuration to defaults."""
    global _config
    _config = None


def is_configured() -> bool:
    """Check if library has been configured."""
    return _config is not None


def print_config() -> None:
    """
    Print current configuration (for debugging).
    
    Examples:
        >>> from simulacrum import print_config
        >>> print_config()
    """
    config = get_config()
    
    print("=" * 60)
    print("SIMULACRUM CONFIGURATION")
    print("=" * 60)
    print(f"LLM Provider:    {config.llm_provider.upper()}")
    print(f"LLM Model:       {config.llm_model}")
    print(f"API Key:         {'✓ Set' if config.llm_api_key else '✗ Not set'}")
    print(f"Temperature:     {config.llm_temperature}")
    print(f"Max Tokens:      {config.llm_max_tokens}")
    print(f"Cache Enabled:   {config.cache_enabled}")
    print(f"Log Level:       {config.log_level}")
    print(f"Debug Mode:      {config.debug_mode}")
    
    if config.extra:
        print("\nExtra Settings:")
        for key, value in config.extra.items():
            print(f"  {key}: {value}")
    
    print("=" * 60)
    print("\nEnvironment Variables:")
    print(f"  OPENAI_API_KEY:     {'✓ Set' if os.getenv('OPENAI_API_KEY') else '✗ Not set'}")
    print(f"  GEMINI_API_KEY:     {'✓ Set' if os.getenv('GEMINI_API_KEY') else '✗ Not set'}")
    print(f"  ANTHROPIC_API_KEY:  {'✓ Set' if os.getenv('ANTHROPIC_API_KEY') else '✗ Not set'}")
    print("=" * 60)


# Convenience functions for quick setup

def use_openai(api_key: Optional[str] = None, model: str = "gpt-4-turbo") -> SimulacrumConfig:
    """
    Quick configure for OpenAI.
    
    Args:
        api_key: OpenAI API key (or use OPENAI_API_KEY env var)
        model: OpenAI model (default: gpt-4-turbo)
        
    Returns:
        SimulacrumConfig
        
    Examples:
        >>> from simulacrum import use_openai
        >>> use_openai(api_key="sk-...")
    """
    return configure(provider="openai", model=model, api_key=api_key)


def use_gemini(api_key: Optional[str] = None, model: str = "gemini-1.5-pro") -> SimulacrumConfig:
    """
    Quick configure for Google Gemini.
    
    Args:
        api_key: Gemini API key (or use GEMINI_API_KEY env var)
        model: Gemini model (default: gemini-1.5-pro)
        
    Returns:
        SimulacrumConfig
        
    Examples:
        >>> from simulacrum import use_gemini
        >>> use_gemini(api_key="...")
    """
    return configure(provider="gemini", model=model, api_key=api_key)


def use_anthropic(api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514") -> SimulacrumConfig:
    """
    Quick configure for Anthropic Claude (optional).
    
    Args:
        api_key: Anthropic API key (or use ANTHROPIC_API_KEY env var)
        model: Claude model (default: claude-sonnet-4-20250514)
        
    Returns:
        SimulacrumConfig
        
    Examples:
        >>> from simulacrum import use_anthropic
        >>> use_anthropic(api_key="sk-ant-...")
    """
    return configure(provider="anthropic", model=model, api_key=api_key)
