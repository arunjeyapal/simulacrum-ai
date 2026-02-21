# src/simulacrum/protocols/__init__.py
"""
Distributed protocols for multi-agent coordination.

Protocols define how agents communicate, coordinate, and reach
collective decisions without centralized control.
"""

from simulacrum.protocols.base import (
    Protocol,
    ProtocolMessage,
    AgentResponse,
    ProtocolState,
    ConsensusType,
    VotingResult
)

from simulacrum.protocols.voting import (
    VotingProtocol,
    quick_vote
)

from simulacrum.protocols.jury import (
    JuryProtocol,
    JuryVerdict,
    simulate_trial
)

__all__ = [
    # Base classes
    "Protocol",
    "ProtocolMessage",
    "AgentResponse",
    "ProtocolState",
    "ConsensusType",
    "VotingResult",
    
    # Voting
    "VotingProtocol",
    "quick_vote",
    
    # Jury
    "JuryProtocol",
    "JuryVerdict",
    "simulate_trial",
]