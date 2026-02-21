# src/simulacrum/protocols/base.py
"""
Base classes for distributed agent protocols.

Protocols define how multiple agents coordinate, communicate, and reach
collective decisions without centralized control.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class ProtocolMessage(BaseModel):
    """A message exchanged between agents in a protocol."""
    sender_id: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    message_type: str = "statement"  # statement, question, vote, proposal
    metadata: Dict[str, Any] = {}


class AgentResponse(BaseModel):
    """An agent's response within a protocol."""
    agent_id: str
    response: str
    confidence: Optional[float] = None  # 0.0-1.0
    reasoning: Optional[str] = None
    vote: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ProtocolState(BaseModel):
    """Current state of a protocol execution."""
    round_number: int = 0
    messages: List[ProtocolMessage] = []
    responses: List[AgentResponse] = []
    metadata: Dict[str, Any] = {}
    is_complete: bool = False
    result: Optional[Any] = None


class Protocol(ABC):
    """
    Abstract base class for all distributed agent protocols.
    
    A protocol defines:
    1. How agents communicate (message format)
    2. What rules govern the interaction (turn-taking, voting)
    3. How collective decisions are reached (consensus mechanism)
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.state = ProtocolState()
    
    @abstractmethod
    def execute(self, agents: List[Any], context: Dict[str, Any]) -> Any:
        """
        Execute the protocol with given agents and context.
        
        Args:
            agents: List of Citizen agents participating
            context: Protocol-specific context (e.g., case details, question)
        
        Returns:
            The collective decision/output of the protocol
        """
        pass
    
    @abstractmethod
    def validate_participation(self, agents: List[Any]) -> bool:
        """
        Validate that agents meet protocol requirements.
        
        For example:
        - Jury needs exactly 12 agents
        - Voting needs at least 2 agents
        - Debate needs exactly 2 agents
        """
        pass
    
    def log_message(self, sender_id: str, content: str, message_type: str = "statement"):
        """Log a message in the protocol state."""
        message = ProtocolMessage(
            sender_id=sender_id,
            content=content,
            message_type=message_type
        )
        self.state.messages.append(message)
    
    def log_response(self, agent_id: str, response: str, **kwargs):
        """Log an agent's response in the protocol state."""
        agent_response = AgentResponse(
            agent_id=agent_id,
            response=response,
            **kwargs
        )
        self.state.responses.append(agent_response)
    
    def get_history(self) -> List[str]:
        """Get formatted history of the protocol execution."""
        history = []
        for msg in self.state.messages:
            history.append(f"[{msg.sender_id}] {msg.content}")
        return history
    
    def reset(self):
        """Reset protocol state for new execution."""
        self.state = ProtocolState()


class ConsensusType(str, Enum):
    """Types of consensus mechanisms."""
    UNANIMOUS = "unanimous"          # All agents must agree
    SIMPLE_MAJORITY = "simple_majority"  # >50% agreement
    SUPERMAJORITY = "supermajority"  # 2/3 or more agreement
    PLURALITY = "plurality"          # Most votes wins (not necessarily >50%)
    WEIGHTED = "weighted"            # Votes weighted by expertise/confidence
    RANKED_CHOICE = "ranked_choice"  # Agents rank preferences


class VotingResult(BaseModel):
    """Result of a voting process."""
    winner: Any
    vote_counts: Dict[str, int]
    total_votes: int
    consensus_type: ConsensusType
    is_decisive: bool  # True if result meets consensus threshold
    tied: bool = False
    confidence: Optional[float] = None
    breakdown: Dict[str, List[str]] = {}  # Option -> list of agent IDs who voted for it