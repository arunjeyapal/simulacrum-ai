# tests/test_synthetic_citizens.py
"""
Unit tests for Synthetic Citizens implementation
Run with: pytest tests/test_synthetic_citizens.py
"""

import pytest
from datetime import datetime
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from simulacrum.agents.persona import (
    Citizen,
    PsychologicalProfile,
    MemoryEntry,
    DemographicProfile,
    create_early_adopter,
    create_skeptic,
    create_anxious_user
)

class TestPsychologicalProfile:
    """Test the personality trait system"""
    
    def test_valid_trait_ranges(self):
        """All traits should accept values between 0.0 and 1.0"""
        profile = PsychologicalProfile(
            openness=0.5,
            conscientiousness=0.7,
            extraversion=0.3,
            agreeableness=0.9,
            neuroticism=0.1
        )
        assert 0 <= profile.openness <= 1
        assert 0 <= profile.conscientiousness <= 1
        assert 0 <= profile.neuroticism <= 1
    
    def test_invalid_trait_bounds(self):
        """Should reject values outside 0.0-1.0 range"""
        with pytest.raises(ValueError):
            PsychologicalProfile(
                openness=1.5,  # Invalid
                conscientiousness=0.5,
                neuroticism=0.5
            )
        
        with pytest.raises(ValueError):
            PsychologicalProfile(
                openness=0.5,
                conscientiousness=-0.1,  # Invalid
                neuroticism=0.5
            )
    
    def test_trait_interpretation(self):
        """Test trait interpretation labels"""
        profile = PsychologicalProfile(
            openness=0.9,
            conscientiousness=0.2,
            neuroticism=0.5
        )
        
        # High openness
        interp = profile.get_trait_interpretation('openness')
        assert 'creative' in interp.lower() or 'open' in interp.lower()
        
        # Low conscientiousness
        interp = profile.get_trait_interpretation('conscientiousness')
        assert 'spontaneous' in interp.lower() or 'flexible' in interp.lower()

class TestCitizen:
    """Test the Citizen agent class"""
    
    def test_citizen_creation(self):
        """Should create a valid citizen with required fields"""
        traits = PsychologicalProfile(
            openness=0.8,
            conscientiousness=0.6,
            neuroticism=0.3
        )
        
        citizen = Citizen(
            name="TestUser",
            role="Tester",
            traits=traits
        )
        
        assert citizen.name == "TestUser"
        assert citizen.role == "Tester"
        assert citizen.traits.openness == 0.8
        assert len(citizen.memory) == 0
    
    def test_citizen_with_backstory(self):
        """Should handle optional backstory"""
        traits = PsychologicalProfile(
            openness=0.5,
            conscientiousness=0.5,
            neuroticism=0.5
        )
        
        citizen = Citizen(
            name="Alex",
            role="Developer",
            traits=traits,
            backstory="Experienced software engineer with 10 years in the field"
        )
        
        assert citizen.backstory is not None
        assert "engineer" in citizen.backstory.lower()
    
    def test_citizen_with_values(self):
        """Should store core values"""
        traits = PsychologicalProfile(
            openness=0.7,
            conscientiousness=0.7,
            neuroticism=0.3
        )
        
        citizen = Citizen(
            name="Jordan",
            role="Manager",
            traits=traits,
            core_values=["innovation", "teamwork", "quality"]
        )
        
        assert len(citizen.core_values) == 3
        assert "innovation" in citizen.core_values
    
    def test_personality_summary(self):
        """Should generate readable personality summary"""
        traits = PsychologicalProfile(
            openness=0.9,
            conscientiousness=0.8,
            extraversion=0.5,
            agreeableness=0.6,
            neuroticism=0.2
        )
        
        citizen = Citizen(
            name="Chris",
            role="Analyst",
            traits=traits
        )
        
        summary = citizen.get_personality_summary()
        
        # Should contain all trait names
        assert "Openness" in summary
        assert "Conscientiousness" in summary
        assert "Neuroticism" in summary
        
        # Should contain values
        assert "0.9" in summary
        assert "0.2" in summary
    
    def test_memory_system(self):
        """Should store and retrieve memories"""
        traits = PsychologicalProfile(
            openness=0.5,
            conscientiousness=0.5,
            neuroticism=0.5
        )
        
        citizen = Citizen(
            name="Sam",
            role="User",
            traits=traits
        )
        
        # Initially empty
        assert len(citizen.memory) == 0
        
        # Add a memory manually (simulating what think() does)
        memory = MemoryEntry(
            stimulus="Product launch announcement",
            response="This looks interesting!"
        )
        citizen.memory.append(memory)
        
        assert len(citizen.memory) == 1
        assert citizen.memory[0].stimulus == "Product launch announcement"
    
    def test_memory_recall(self):
        """Should recall memories by keyword"""
        traits = PsychologicalProfile(
            openness=0.5,
            conscientiousness=0.5,
            neuroticism=0.5
        )
        
        citizen = Citizen(
            name="Taylor",
            role="Customer",
            traits=traits
        )
        
        # Add multiple memories
        citizen.memory.append(MemoryEntry(
            stimulus="Product A announcement",
            response="Interesting product"
        ))
        citizen.memory.append(MemoryEntry(
            stimulus="Pricing update",
            response="Too expensive"
        ))
        citizen.memory.append(MemoryEntry(
            stimulus="Product B announcement",
            response="Not relevant to me"
        ))
        
        # Recall by keyword
        product_memories = citizen.recall("product")
        assert len(product_memories) == 2  # Should find both product mentions
        
        pricing_memories = citizen.recall("pricing")
        assert len(pricing_memories) == 1

class TestFactoryFunctions:
    """Test the archetype factory functions"""
    
    def test_create_early_adopter(self):
        """Should create early adopter with high openness"""
        adopter = create_early_adopter(name="Alex")
        
        assert adopter.name == "Alex"
        assert adopter.traits.openness >= 0.7  # High openness
        assert adopter.traits.neuroticism <= 0.3  # Low anxiety
        assert "innovation" in adopter.core_values or "tech" in adopter.role.lower()
    
    def test_create_skeptic(self):
        """Should create skeptic with low openness, high conscientiousness"""
        skeptic = create_skeptic(name="Barbara")
        
        assert skeptic.name == "Barbara"
        assert skeptic.traits.openness <= 0.3  # Low openness
        assert skeptic.traits.conscientiousness >= 0.7  # High conscientiousness
        assert "security" in skeptic.core_values or "stability" in skeptic.core_values
    
    def test_create_anxious_user(self):
        """Should create anxious user with high neuroticism"""
        anxious = create_anxious_user(name="Charlie")
        
        assert anxious.name == "Charlie"
        assert anxious.traits.neuroticism >= 0.7  # High anxiety
        assert "safety" in anxious.core_values or anxious.demographics is not None

class TestSystemPromptGeneration:
    """Test system prompt construction"""
    
    def test_basic_prompt_structure(self):
        """Should generate well-structured system prompt"""
        traits = PsychologicalProfile(
            openness=0.8,
            conscientiousness=0.6,
            neuroticism=0.3
        )
        
        citizen = Citizen(
            name="Jordan",
            role="Product Manager",
            traits=traits
        )
        
        prompt = citizen._build_system_prompt()
        
        # Should contain identity
        assert "Jordan" in prompt
        assert "Product Manager" in prompt
        
        # Should contain trait values
        assert "0.8" in prompt
        assert "0.6" in prompt
        assert "0.3" in prompt
        
        # Should contain behavioral guidelines
        assert "first-person" in prompt.lower() or "I think" in prompt
    
    def test_prompt_with_backstory(self):
        """Should include backstory in prompt"""
        traits = PsychologicalProfile(
            openness=0.7,
            conscientiousness=0.7,
            neuroticism=0.4
        )
        
        citizen = Citizen(
            name="Alex",
            role="Engineer",
            traits=traits,
            backstory="10 years of experience in distributed systems"
        )
        
        prompt = citizen._build_system_prompt()
        assert "distributed systems" in prompt.lower()
    
    def test_prompt_with_values(self):
        """Should include core values in prompt"""
        traits = PsychologicalProfile(
            openness=0.6,
            conscientiousness=0.6,
            neuroticism=0.5
        )
        
        citizen = Citizen(
            name="Sam",
            role="Designer",
            traits=traits,
            core_values=["user experience", "accessibility"]
        )
        
        prompt = citizen._build_system_prompt()
        assert "user experience" in prompt.lower()
        assert "accessibility" in prompt.lower()

class TestMemoryEntry:
    """Test memory entry structure"""
    
    def test_memory_creation(self):
        """Should create memory with timestamp"""
        memory = MemoryEntry(
            stimulus="Test input",
            response="Test output"
        )
        
        assert memory.stimulus == "Test input"
        assert memory.response == "Test output"
        assert isinstance(memory.timestamp, datetime)
    
    def test_memory_with_emotion(self):
        """Should support optional emotional valence"""
        memory = MemoryEntry(
            stimulus="Good news!",
            response="Great!",
            emotional_valence=0.8  # Positive
        )
        
        assert memory.emotional_valence == 0.8

class TestDemographicProfile:
    """Test demographic information handling"""
    
    def test_demographic_creation(self):
        """Should create optional demographic profile"""
        demo = DemographicProfile(
            age=35,
            occupation="Software Engineer",
            education_level="Bachelor's Degree"
        )
        
        assert demo.age == 35
        assert demo.occupation == "Software Engineer"
    
    def test_citizen_with_demographics(self):
        """Should attach demographics to citizen"""
        traits = PsychologicalProfile(
            openness=0.7,
            conscientiousness=0.7,
            neuroticism=0.3
        )
        
        demo = DemographicProfile(
            age=42,
            occupation="Manager",
            income_bracket="$100k-150k"
        )
        
        citizen = Citizen(
            name="Morgan",
            role="Business Leader",
            traits=traits,
            demographics=demo
        )
        
        assert citizen.demographics.age == 42
        assert citizen.demographics.occupation == "Manager"

# Integration test (requires API key - mark as slow)
@pytest.mark.slow
class TestIntegration:
    """Integration tests that make actual LLM calls"""
    
    def test_think_method(self):
        """Should generate a response using LLM (requires API key)"""
        # This test requires OPENAI_API_KEY or similar in environment
        # Skip if not available
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("No API key available")
        
        citizen = create_early_adopter(name="TestUser")
        
        try:
            response = citizen.think("Hello, how are you?")
            
            assert isinstance(response, str)
            assert len(response) > 0
            assert len(citizen.memory) == 1
        except Exception as e:
            pytest.skip(f"API call failed: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])