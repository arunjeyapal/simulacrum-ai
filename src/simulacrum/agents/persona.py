# src/simulacrum/agents/persona.py

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from simulacrum.core.llm import LLMEngine

class PsychologicalProfile(BaseModel):
    """
    Big Five personality traits (OCEAN model)
    Each trait ranges from 0.0 (low) to 1.0 (high)
    """
    openness: float = Field(..., ge=0, le=1, description="Willingness to try new things, creativity")
    conscientiousness: float = Field(..., ge=0, le=1, description="Discipline, organization, reliability")
    extraversion: float = Field(0.5, ge=0, le=1, description="Social energy, assertiveness")
    agreeableness: float = Field(0.5, ge=0, le=1, description="Cooperation, empathy, trust")
    neuroticism: float = Field(..., ge=0, le=1, description="Emotional instability, anxiety, stress response")
    
    def get_trait_interpretation(self, trait_name: str) -> str:
        """Provide human-readable interpretation of trait levels"""
        value = getattr(self, trait_name.lower())
        
        interpretations = {
            "openness": {
                "high": "creative, curious, open to new experiences",
                "medium": "moderately open to new ideas",
                "low": "traditional, prefers routine, resistant to change"
            },
            "conscientiousness": {
                "high": "organized, disciplined, detail-oriented",
                "medium": "moderately organized",
                "low": "spontaneous, flexible, less concerned with planning"
            },
            "extraversion": {
                "high": "outgoing, energetic, seeks social interaction",
                "medium": "balanced between social and solitary activities",
                "low": "reserved, introspective, prefers solitude"
            },
            "agreeableness": {
                "high": "cooperative, empathetic, trusting",
                "medium": "moderately cooperative",
                "low": "competitive, skeptical, direct"
            },
            "neuroticism": {
                "high": "anxious, emotionally reactive, stress-prone",
                "medium": "moderately emotionally stable",
                "low": "calm, emotionally stable, resilient"
            }
        }
        
        level = "high" if value > 0.65 else "low" if value < 0.35 else "medium"
        return interpretations.get(trait_name.lower(), {}).get(level, "undefined")

class MemoryEntry(BaseModel):
    """Single memory record with metadata"""
    timestamp: datetime = Field(default_factory=datetime.now)
    stimulus: str
    response: str
    emotional_valence: Optional[float] = None  # -1 (negative) to +1 (positive)
    
class DemographicProfile(BaseModel):
    """Optional demographic information for richer simulation"""
    age: Optional[int] = None
    occupation: Optional[str] = None
    education_level: Optional[str] = None
    income_bracket: Optional[str] = None
    geographic_region: Optional[str] = None

class Citizen(BaseModel):
    """
    A Synthetic Citizen: An AI agent with psychological consistency,
    memory, and behavioral patterns that simulate human decision-making.
    """
    name: str
    role: str
    traits: PsychologicalProfile
    demographics: Optional[DemographicProfile] = None
    backstory: Optional[str] = None
    
    # Memory systems
    memory: List[MemoryEntry] = []
    core_values: List[str] = []  # e.g., ["security", "innovation", "family"]
    
    # LLM configuration
    model: str = "openai/gpt-3.5-turbo"
    temperature: float = 0.8
    
    # Behavioral flags
    verbose_thinking: bool = False  # If True, returns chain of thought
    
    class Config:
        arbitrary_types_allowed = True
        extra = 'allow'
    
    def get_personality_summary(self) -> str:
        """Generate a human-readable personality description"""
        traits_desc = []
        for trait in ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]:
            value = getattr(self.traits, trait)
            interp = self.traits.get_trait_interpretation(trait)
            traits_desc.append(f"{trait.capitalize()}: {value:.1f} ({interp})")
        
        return "\n".join(traits_desc)
    
    def _build_system_prompt(self) -> str:
        """Construct the system prompt that defines the agent's identity"""
        prompt_parts = [
            f"You are {self.name}, a {self.role}.",
            "",
            "PERSONALITY PROFILE (0.0-1.0 scale):",
            f"- Openness: {self.traits.openness} ({self.traits.get_trait_interpretation('openness')})",
            f"- Conscientiousness: {self.traits.conscientiousness} ({self.traits.get_trait_interpretation('conscientiousness')})",
            f"- Extraversion: {self.traits.extraversion} ({self.traits.get_trait_interpretation('extraversion')})",
            f"- Agreeableness: {self.traits.agreeableness} ({self.traits.get_trait_interpretation('agreeableness')})",
            f"- Neuroticism: {self.traits.neuroticism} ({self.traits.get_trait_interpretation('neuroticism')})",
        ]
        
        if self.backstory:
            prompt_parts.extend(["", f"BACKSTORY: {self.backstory}"])
        
        if self.core_values:
            values_str = ", ".join(self.core_values)
            prompt_parts.extend(["", f"CORE VALUES: {values_str}"])
        
        if self.demographics:
            demo_parts = []
            if self.demographics.age:
                demo_parts.append(f"Age: {self.demographics.age}")
            if self.demographics.occupation:
                demo_parts.append(f"Occupation: {self.demographics.occupation}")
            if demo_parts:
                prompt_parts.extend(["", "DEMOGRAPHICS:", "- " + "\n- ".join(demo_parts)])
        
        prompt_parts.extend([
            "",
            "BEHAVIORAL GUIDELINES:",
            "1. Your response must reflect your personality traits consistently",
            "2. React authentically as this person would—not as a neutral AI",
            "3. Use first-person perspective ('I think...' not 'As [name]...')",
            "4. Keep responses concise and natural (1-3 sentences)",
            "5. Show emotional reactions aligned with your neuroticism level",
        ])
        
        if self.verbose_thinking:
            prompt_parts.append("6. Begin with [THINKING: ...] to show your reasoning process")
        
        return "\n".join(prompt_parts)
    
    def think(self, stimulus: str, context: Optional[str] = None) -> str:
        """
        Core cognitive loop: Stimulus → Internal Processing → Response
        
        Args:
            stimulus: The input/event the citizen is reacting to
            context: Optional additional context (e.g., "This is a product announcement")
        
        Returns:
            The citizen's authentic reaction
        """
        engine = LLMEngine(model_name=self.model)
        
        system_prompt = self._build_system_prompt()
        
        # Build user prompt with optional context and memory
        user_prompt_parts = []
        
        if context:
            user_prompt_parts.append(f"CONTEXT: {context}\n")
        
        # Include recent memory if available (last 3 interactions)
        if self.memory:
            recent_memories = self.memory[-3:]
            user_prompt_parts.append("RECENT MEMORY:")
            for mem in recent_memories:
                user_prompt_parts.append(f"- You encountered: '{mem.stimulus}' and responded: '{mem.response}'")
            user_prompt_parts.append("")
        
        user_prompt_parts.append(f"CURRENT STIMULUS:\n{stimulus}")
        user_prompt_parts.append("\nHow do you react?")
        
        user_prompt = "\n".join(user_prompt_parts)
        
        # Generate response
        response = engine.generate(system_prompt, user_prompt, temperature=self.temperature)
        
        # Store in memory
        memory_entry = MemoryEntry(
            stimulus=stimulus,
            response=response
        )
        self.memory.append(memory_entry)
        
        return response
    
    def remember(self, event: str, context: str = "") -> None:
        """Store an event directly in memory without LLM processing."""
        self.memory.append(MemoryEntry(
            stimulus=event,
            response=context or "noted"
        ))

    def recall(self, keyword: str) -> List[MemoryEntry]:
        """Retrieve memories containing a specific keyword"""
        return [
            mem for mem in self.memory
            if keyword.lower() in mem.stimulus.lower() or keyword.lower() in mem.response.lower()
        ]
    
    def get_memory_summary(self) -> str:
        """Generate a summary of interaction history"""
        if not self.memory:
            return "No interactions yet."
        
        return f"Total interactions: {len(self.memory)}\n" + \
               f"First interaction: {self.memory[0].timestamp.strftime('%Y-%m-%d %H:%M')}\n" + \
               f"Last interaction: {self.memory[-1].timestamp.strftime('%Y-%m-%d %H:%M')}"


# Factory functions for common archetypes
def create_early_adopter(name: str = "Alex", model: str = "openai/gpt-3.5-turbo") -> Citizen:
    """Factory function for Early Adopter archetype"""
    return Citizen(
        name=name,
        role="Tech Enthusiast & Early Adopter",
        traits=PsychologicalProfile(
            openness=0.9,
            conscientiousness=0.4,
            extraversion=0.7,
            agreeableness=0.6,
            neuroticism=0.2
        ),
        core_values=["innovation", "efficiency", "progress"],
        backstory="Always the first to try new technology. Reads tech blogs daily and participates in beta programs.",
        model=model
    )

def create_skeptic(name: str = "Barbara", model: str = "openai/gpt-3.5-turbo") -> Citizen:
    """Factory function for Skeptic archetype"""
    return Citizen(
        name=name,
        role="Risk Analyst & Skeptic",
        traits=PsychologicalProfile(
            openness=0.2,
            conscientiousness=0.9,
            extraversion=0.3,
            agreeableness=0.4,
            neuroticism=0.5
        ),
        core_values=["security", "stability", "diligence"],
        backstory="Former auditor with 15 years experience. Believes in thorough due diligence before any decision.",
        model=model
    )

def create_anxious_user(name: str = "Charlie", model: str = "openai/gpt-3.5-turbo") -> Citizen:
    """Factory function for Anxious User archetype"""
    return Citizen(
        name=name,
        role="Retiree & Conservative Investor",
        traits=PsychologicalProfile(
            openness=0.3,
            conscientiousness=0.6,
            extraversion=0.4,
            agreeableness=0.7,
            neuroticism=0.9
        ),
        core_values=["safety", "family", "peace of mind"],
        backstory="Recently retired after 35 years. Very protective of retirement savings. Prefers proven, stable approaches.",
        demographics=DemographicProfile(age=67, occupation="Retired Teacher"),
        model=model
    )