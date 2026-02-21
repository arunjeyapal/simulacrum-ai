# src/simulacrum/protocols/voting.py
"""
Voting protocols for distributed agent decision-making.

Implements various voting mechanisms:
- Simple Majority (>50%)
- Supermajority (2/3+)
- Unanimous
- Weighted by confidence
- Ranked choice
"""

from typing import List, Dict, Any, Optional, Tuple
from collections import Counter, defaultdict
from simulacrum.protocols.base import (
    Protocol, 
    ConsensusType, 
    VotingResult,
    ProtocolMessage
)


class VotingProtocol(Protocol):
    """
    Voting protocol for collective decision-making.
    
    Agents are presented with options and vote based on their
    psychological profiles and reasoning.
    """
    
    def __init__(
        self,
        consensus_type: ConsensusType = ConsensusType.SIMPLE_MAJORITY,
        allow_abstention: bool = False,
        require_reasoning: bool = True
    ):
        super().__init__(
            name="Voting Protocol",
            description=f"Collective decision via {consensus_type.value} voting"
        )
        self.consensus_type = consensus_type
        self.allow_abstention = allow_abstention
        self.require_reasoning = require_reasoning
    
    def validate_participation(self, agents: List[Any]) -> bool:
        """Requires at least 2 agents to vote."""
        return len(agents) >= 2
    
    def execute(
        self,
        agents: List[Any],
        context: Dict[str, Any]
    ) -> VotingResult:
        """
        Execute voting protocol.
        
        Context should contain:
        - question: The decision to be made
        - options: List of choices
        - background: Additional context (optional)
        """
        if not self.validate_participation(agents):
            raise ValueError("Voting requires at least 2 agents")
        
        question = context.get("question", "")
        options = context.get("options", [])
        background = context.get("background", "")
        
        if not options:
            raise ValueError("Voting requires options to choose from")
        
        # Round 1: Collect votes
        votes = self._collect_votes(agents, question, options, background)
        
        # Calculate result based on consensus type
        result = self._calculate_result(votes, agents)
        
        self.state.result = result
        self.state.is_complete = True
        
        return result
    
    def _collect_votes(
        self,
        agents: List[Any],
        question: str,
        options: List[str],
        background: str
    ) -> List[Dict[str, Any]]:
        """Collect votes from all agents."""
        votes = []
        
        # Build the voting prompt
        options_str = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
        
        prompt = f"{background}\n\n" if background else ""
        prompt += f"QUESTION: {question}\n\n"
        prompt += f"OPTIONS:\n{options_str}\n\n"
        
        if self.require_reasoning:
            prompt += "Respond with:\n"
            prompt += "1. Your choice (just the number)\n"
            prompt += "2. Your reasoning (1-2 sentences)\n"
            prompt += "Format: 'VOTE: [number]\\nREASON: [your reasoning]'"
        else:
            prompt += "Respond with just the number of your choice (1, 2, 3, etc.)"
        
        for agent in agents:
            # Agent deliberates and votes
            response = agent.think(prompt, context="Voting decision")
            
            # Parse vote and reasoning
            vote_data = self._parse_vote(response, options)
            vote_data["agent_id"] = agent.name
            vote_data["agent"] = agent
            
            votes.append(vote_data)
            
            # Log in protocol state
            self.log_response(
                agent_id=agent.name,
                response=response,
                vote=vote_data["choice"],
                reasoning=vote_data.get("reasoning")
            )
        
        return votes
    
    def _parse_vote(self, response: str, options: List[str]) -> Dict[str, Any]:
        """Parse agent's vote from their response."""
        vote_data = {
            "choice": None,
            "reasoning": None,
            "raw_response": response
        }
        
        # Try to extract structured vote
        if "VOTE:" in response.upper():
            lines = response.split("\n")
            for i, line in enumerate(lines):
                if "VOTE:" in line.upper():
                    # Extract vote number
                    vote_str = line.split(":", 1)[1].strip()
                    try:
                        vote_num = int(''.join(filter(str.isdigit, vote_str)))
                        if 1 <= vote_num <= len(options):
                            vote_data["choice"] = options[vote_num - 1]
                    except:
                        pass
                
                if "REASON:" in line.upper() and i < len(lines):
                    # Extract reasoning
                    reason_str = line.split(":", 1)[1].strip()
                    if not reason_str and i + 1 < len(lines):
                        reason_str = lines[i + 1].strip()
                    vote_data["reasoning"] = reason_str
        
        # Fallback: try to find option mentioned in response
        if not vote_data["choice"]:
            response_lower = response.lower()
            for option in options:
                if option.lower() in response_lower:
                    vote_data["choice"] = option
                    break
        
        # Last resort: try to find a number
        if not vote_data["choice"]:
            for i, option in enumerate(options, 1):
                if str(i) in response[:50]:  # Check first 50 chars
                    vote_data["choice"] = option
                    break
        
        # If still no vote, mark as abstention
        if not vote_data["choice"]:
            vote_data["choice"] = "ABSTAIN" if self.allow_abstention else options[0]
        
        return vote_data
    
    def _calculate_result(
        self,
        votes: List[Dict[str, Any]],
        agents: List[Any]
    ) -> VotingResult:
        """Calculate voting result based on consensus type."""
        
        # Count votes
        vote_counts = Counter([v["choice"] for v in votes])
        total_votes = len(votes)
        
        # Build breakdown
        breakdown = defaultdict(list)
        for vote in votes:
            breakdown[vote["choice"]].append(vote["agent_id"])
        
        # Determine winner based on consensus type
        if self.consensus_type == ConsensusType.SIMPLE_MAJORITY:
            return self._simple_majority(vote_counts, total_votes, dict(breakdown))
        
        elif self.consensus_type == ConsensusType.SUPERMAJORITY:
            return self._supermajority(vote_counts, total_votes, dict(breakdown))
        
        elif self.consensus_type == ConsensusType.UNANIMOUS:
            return self._unanimous(vote_counts, total_votes, dict(breakdown))
        
        elif self.consensus_type == ConsensusType.PLURALITY:
            return self._plurality(vote_counts, total_votes, dict(breakdown))
        
        elif self.consensus_type == ConsensusType.WEIGHTED:
            return self._weighted(votes, dict(breakdown))
        
        else:
            return self._simple_majority(vote_counts, total_votes, dict(breakdown))
    
    def _simple_majority(
        self,
        vote_counts: Counter,
        total_votes: int,
        breakdown: Dict
    ) -> VotingResult:
        """Simple majority: >50% of votes."""
        winner, max_votes = vote_counts.most_common(1)[0]
        required = total_votes / 2
        is_decisive = max_votes > required
        
        # Check for tie
        top_two = vote_counts.most_common(2)
        tied = len(top_two) > 1 and top_two[0][1] == top_two[1][1]
        
        return VotingResult(
            winner=winner,
            vote_counts=dict(vote_counts),
            total_votes=total_votes,
            consensus_type=ConsensusType.SIMPLE_MAJORITY,
            is_decisive=is_decisive and not tied,
            tied=tied,
            confidence=max_votes / total_votes if not tied else 0.5,
            breakdown=breakdown
        )
    
    def _supermajority(
        self,
        vote_counts: Counter,
        total_votes: int,
        breakdown: Dict
    ) -> VotingResult:
        """Supermajority: 2/3 or more of votes."""
        winner, max_votes = vote_counts.most_common(1)[0]
        required = (2 * total_votes) / 3
        is_decisive = max_votes >= required
        
        return VotingResult(
            winner=winner,
            vote_counts=dict(vote_counts),
            total_votes=total_votes,
            consensus_type=ConsensusType.SUPERMAJORITY,
            is_decisive=is_decisive,
            tied=False,
            confidence=max_votes / total_votes,
            breakdown=breakdown
        )
    
    def _unanimous(
        self,
        vote_counts: Counter,
        total_votes: int,
        breakdown: Dict
    ) -> VotingResult:
        """Unanimous: All agents must agree."""
        winner, max_votes = vote_counts.most_common(1)[0]
        is_decisive = max_votes == total_votes
        
        return VotingResult(
            winner=winner,
            vote_counts=dict(vote_counts),
            total_votes=total_votes,
            consensus_type=ConsensusType.UNANIMOUS,
            is_decisive=is_decisive,
            tied=False,
            confidence=1.0 if is_decisive else max_votes / total_votes,
            breakdown=breakdown
        )
    
    def _plurality(
        self,
        vote_counts: Counter,
        total_votes: int,
        breakdown: Dict
    ) -> VotingResult:
        """Plurality: Most votes wins (no majority required)."""
        winner, max_votes = vote_counts.most_common(1)[0]
        
        # Check for tie
        top_two = vote_counts.most_common(2)
        tied = len(top_two) > 1 and top_two[0][1] == top_two[1][1]
        
        return VotingResult(
            winner=winner,
            vote_counts=dict(vote_counts),
            total_votes=total_votes,
            consensus_type=ConsensusType.PLURALITY,
            is_decisive=not tied,
            tied=tied,
            confidence=max_votes / total_votes,
            breakdown=breakdown
        )
    
    def _weighted(
        self,
        votes: List[Dict[str, Any]],
        breakdown: Dict
    ) -> VotingResult:
        """Weighted voting based on agent confidence/expertise."""
        # Weight by agent conscientiousness (proxy for careful decision-making)
        weighted_votes = defaultdict(float)
        
        for vote in votes:
            choice = vote["choice"]
            agent = vote["agent"]
            
            # Weight by conscientiousness (more careful = more weight)
            weight = agent.traits.conscientiousness
            weighted_votes[choice] += weight
        
        winner = max(weighted_votes, key=weighted_votes.get)
        total_weight = sum(weighted_votes.values())
        
        return VotingResult(
            winner=winner,
            vote_counts={k: int(v * 10) for k, v in weighted_votes.items()},  # Scale for display
            total_votes=len(votes),
            consensus_type=ConsensusType.WEIGHTED,
            is_decisive=True,
            tied=False,
            confidence=weighted_votes[winner] / total_weight,
            breakdown=breakdown
        )


def quick_vote(
    agents: List[Any],
    question: str,
    options: List[str],
    consensus_type: ConsensusType = ConsensusType.SIMPLE_MAJORITY
) -> VotingResult:
    """
    Convenience function for quick voting.
    
    Example:
        result = quick_vote(
            agents=[alex, barbara, charlie],
            question="Should we increase prices?",
            options=["Yes", "No", "Needs more research"]
        )
    """
    protocol = VotingProtocol(consensus_type=consensus_type)
    return protocol.execute(
        agents=agents,
        context={
            "question": question,
            "options": options
        }
    )