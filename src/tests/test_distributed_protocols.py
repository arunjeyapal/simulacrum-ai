# tests/test_protocols.py
"""
Unit tests for distributed protocol implementations
Run with: pytest tests/test_protocols.py
"""

import pytest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from simulacrum.agents.persona import (
    Citizen,
    PsychologicalProfile,
    create_early_adopter,
    create_skeptic,
    create_anxious_user
)
from simulacrum.protocols.base import (
    Protocol,
    ConsensusType,
    ProtocolState
)
from simulacrum.protocols.voting import VotingProtocol, quick_vote
from simulacrum.protocols.jury import JuryProtocol, simulate_trial


class TestVotingProtocol:
    """Test voting protocol functionality"""
    
    def test_voting_protocol_creation(self):
        """Should create voting protocol with different consensus types"""
        protocol = VotingProtocol(ConsensusType.SIMPLE_MAJORITY)
        assert protocol.consensus_type == ConsensusType.SIMPLE_MAJORITY
        
        protocol2 = VotingProtocol(ConsensusType.SUPERMAJORITY)
        assert protocol2.consensus_type == ConsensusType.SUPERMAJORITY
    
    def test_validate_participation(self):
        """Should require at least 2 agents"""
        protocol = VotingProtocol()
        
        # Too few agents
        assert not protocol.validate_participation([])
        assert not protocol.validate_participation([create_early_adopter()])
        
        # Valid number
        assert protocol.validate_participation([
            create_early_adopter(),
            create_skeptic()
        ])
    
    def test_vote_parsing(self):
        """Should parse votes from natural language responses"""
        protocol = VotingProtocol()
        options = ["Option A", "Option B", "Option C"]
        
        # Structured format
        response1 = "VOTE: 1\nREASON: I think Option A is best"
        vote1 = protocol._parse_vote(response1, options)
        assert vote1["choice"] == "Option A"
        
        # Keyword in response
        response2 = "I prefer Option B because it's safer"
        vote2 = protocol._parse_vote(response2, options)
        assert vote2["choice"] == "Option B"
    
    def test_simple_majority(self):
        """Should calculate simple majority correctly"""
        protocol = VotingProtocol(ConsensusType.SIMPLE_MAJORITY)
        
        from collections import Counter
        votes = Counter({"Option A": 3, "Option B": 2})
        result = protocol._simple_majority(votes, 5, {"Option A": ["a1", "a2", "a3"], "Option B": ["b1", "b2"]})
        
        assert result.winner == "Option A"
        assert result.is_decisive == True
        assert result.confidence == 0.6
    
    def test_supermajority(self):
        """Should calculate supermajority correctly"""
        protocol = VotingProtocol(ConsensusType.SUPERMAJORITY)
        
        from collections import Counter
        # Not enough for supermajority (60% < 66.7%)
        votes1 = Counter({"Option A": 3, "Option B": 2})
        result1 = protocol._supermajority(votes1, 5, {})
        assert result1.is_decisive == False
        
        # Enough for supermajority (4/6 = 66.7%)
        votes2 = Counter({"Option A": 4, "Option B": 2})
        result2 = protocol._supermajority(votes2, 6, {})
        assert result2.is_decisive == True
    
    def test_unanimous(self):
        """Should require all agents to agree"""
        protocol = VotingProtocol(ConsensusType.UNANIMOUS)
        
        from collections import Counter
        # Unanimous
        votes1 = Counter({"Option A": 5})
        result1 = protocol._unanimous(votes1, 5, {})
        assert result1.is_decisive == True
        assert result1.confidence == 1.0
        
        # Not unanimous
        votes2 = Counter({"Option A": 4, "Option B": 1})
        result2 = protocol._unanimous(votes2, 5, {})
        assert result2.is_decisive == False
    
    def test_tie_detection(self):
        """Should detect ties"""
        protocol = VotingProtocol(ConsensusType.SIMPLE_MAJORITY)
        
        from collections import Counter
        votes = Counter({"Option A": 2, "Option B": 2})
        result = protocol._simple_majority(votes, 4, {})
        
        assert result.tied == True
        assert result.is_decisive == False


class TestJuryProtocol:
    """Test jury deliberation protocol"""
    
    def test_jury_protocol_creation(self):
        """Should create jury protocol with parameters"""
        protocol = JuryProtocol(max_rounds=3, required_consensus=0.75)
        assert protocol.max_rounds == 3
        assert protocol.required_consensus == 0.75
    
    def test_validate_participation(self):
        """Should require 6-12 jurors"""
        protocol = JuryProtocol()
        
        # Too few
        agents_5 = [create_early_adopter() for _ in range(5)]
        assert not protocol.validate_participation(agents_5)
        
        # Valid
        agents_6 = [create_early_adopter() for _ in range(6)]
        assert protocol.validate_participation(agents_6)
        
        agents_12 = [create_early_adopter() for _ in range(12)]
        assert protocol.validate_participation(agents_12)
        
        # Too many
        agents_13 = [create_early_adopter() for _ in range(13)]
        assert not protocol.validate_participation(agents_13)
    
    def test_jury_vote_parsing(self):
        """Should parse guilty/not guilty votes"""
        protocol = JuryProtocol()
        options = ["Guilty", "Not Guilty"]
        
        # Explicit guilty
        response1 = "VOTE: Guilty\nREASON: The evidence is clear"
        vote1 = protocol._parse_jury_vote(response1, options)
        assert vote1 == "Guilty"
        
        # Explicit not guilty
        response2 = "VOTE: Not Guilty\nREASON: Reasonable doubt exists"
        vote2 = protocol._parse_jury_vote(response2, options)
        assert vote2 == "Not Guilty"
        
        # In text
        response3 = "I believe the defendant is not guilty"
        vote3 = protocol._parse_jury_vote(response3, options)
        assert vote3 == "Not Guilty"
    
    def test_consensus_check(self):
        """Should check consensus correctly"""
        protocol = JuryProtocol(required_consensus=0.75)
        
        # Meets consensus (9/12 = 75%)
        votes1 = {"Guilty": 9, "Not Guilty": 3}
        assert protocol._check_consensus(votes1, 12) == True
        
        # Doesn't meet consensus (8/12 = 66.7%)
        votes2 = {"Guilty": 8, "Not Guilty": 4}
        assert protocol._check_consensus(votes2, 12) == False


class TestQuickVote:
    """Test convenience functions"""
    
    @pytest.mark.slow
    def test_quick_vote_integration(self):
        """Integration test with real agents (requires API key)"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("No API key available")
        
        agents = [
            create_early_adopter(name="Alex"),
            create_skeptic(name="Barbara"),
            create_anxious_user(name="Charlie")
        ]
        
        try:
            result = quick_vote(
                agents=agents,
                question="Should we proceed?",
                options=["Yes", "No"]
            )
            
            assert result.winner in ["Yes", "No"]
            assert result.total_votes == 3
            assert isinstance(result.vote_counts, dict)
        except Exception as e:
            pytest.skip(f"API call failed: {e}")


class TestProtocolState:
    """Test protocol state management"""
    
    def test_protocol_state_creation(self):
        """Should create empty protocol state"""
        state = ProtocolState()
        assert state.round_number == 0
        assert len(state.messages) == 0
        assert len(state.responses) == 0
        assert state.is_complete == False
    
    def test_message_logging(self):
        """Should log messages correctly"""
        protocol = VotingProtocol()
        
        protocol.log_message("agent1", "I vote yes", "vote")
        assert len(protocol.state.messages) == 1
        assert protocol.state.messages[0].sender_id == "agent1"
        assert protocol.state.messages[0].content == "I vote yes"
    
    def test_response_logging(self):
        """Should log responses correctly"""
        protocol = VotingProtocol()
        
        protocol.log_response("agent1", "Yes", vote="Yes")
        assert len(protocol.state.responses) == 1
        assert protocol.state.responses[0].agent_id == "agent1"
        assert protocol.state.responses[0].vote == "Yes"
    
    def test_protocol_reset(self):
        """Should reset protocol state"""
        protocol = VotingProtocol()
        
        protocol.log_message("agent1", "Test")
        protocol.log_response("agent1", "Response")
        
        protocol.reset()
        
        assert len(protocol.state.messages) == 0
        assert len(protocol.state.responses) == 0


class TestConsensusTypes:
    """Test consensus type enumeration"""
    
    def test_consensus_type_values(self):
        """Should have all consensus types"""
        assert ConsensusType.SIMPLE_MAJORITY.value == "simple_majority"
        assert ConsensusType.SUPERMAJORITY.value == "supermajority"
        assert ConsensusType.UNANIMOUS.value == "unanimous"
        assert ConsensusType.PLURALITY.value == "plurality"
        assert ConsensusType.WEIGHTED.value == "weighted"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])