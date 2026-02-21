# src/simulacrum/protocols/jury.py
"""
Jury deliberation protocol for complex decision-making.

Simulates a jury process:
1. Initial private votes
2. Group discussion rounds
3. Opinion shifts based on arguments
4. Final verdict with consensus tracking
"""

from typing import List, Dict, Any, Optional
from collections import Counter
from simulacrum.protocols.base import Protocol, ProtocolMessage
from simulacrum.protocols.voting import VotingProtocol, ConsensusType
from pydantic import BaseModel


class JuryVerdict(BaseModel):
    """Final verdict from jury deliberation."""
    verdict: str  # "Guilty", "Not Guilty", "Hung Jury"
    final_vote_counts: Dict[str, int]
    rounds_taken: int
    consensus_reached: bool
    vote_trajectory: List[Dict[str, int]]  # How votes changed each round
    key_arguments: List[str]  # Most influential arguments
    holdouts: List[str] = []  # Agents who never changed position


class JuryProtocol(Protocol):
    """
    Jury deliberation protocol with multi-round discussion.
    
    Models realistic jury dynamics:
    - Initial secret votes
    - Open discussion with argument exchange
    - Vote shifts based on persuasion
    - Consensus building or hung jury declaration
    """
    
    def __init__(
        self,
        max_rounds: int = 5,
        required_consensus: float = 0.75,  # 9/12 for unanimous-leaning
        allow_hung_jury: bool = True
    ):
        super().__init__(
            name="Jury Deliberation",
            description="Multi-round deliberation with consensus building"
        )
        self.max_rounds = max_rounds
        self.required_consensus = required_consensus
        self.allow_hung_jury = allow_hung_jury
    
    def validate_participation(self, agents: List[Any]) -> bool:
        """Traditionally requires 12 jurors, but flexible for simulation."""
        return 6 <= len(agents) <= 12
    
    def execute(
        self,
        agents: List[Any],
        context: Dict[str, Any]
    ) -> JuryVerdict:
        """
        Execute jury deliberation.
        
        Context should contain:
        - case_summary: Description of the case
        - evidence: Key pieces of evidence
        - charges: What the defendant is charged with
        - verdict_options: Usually ["Guilty", "Not Guilty"]
        """
        if not self.validate_participation(agents):
            raise ValueError(f"Jury requires 6-12 agents, got {len(agents)}")
        
        case_summary = context.get("case_summary", "")
        evidence = context.get("evidence", [])
        charges = context.get("charges", "")
        verdict_options = context.get("verdict_options", ["Guilty", "Not Guilty"])
        
        # Track voting trajectory
        vote_trajectory = []
        key_arguments = []
        agent_positions = {agent.name: None for agent in agents}
        
        # Round 0: Initial secret votes
        print(f"\n[Jury Deliberation] Case: {charges}")
        print(f"[Jury Deliberation] {len(agents)} jurors empaneled")
        
        current_votes = self._initial_vote(agents, case_summary, evidence, charges, verdict_options)
        vote_trajectory.append(current_votes)
        
        # Update positions
        for agent in agents:
            for response in self.state.responses:
                if response.agent_id == agent.name and response.vote:
                    agent_positions[agent.name] = response.vote
                    break
        
        # Check if already unanimous
        if self._check_consensus(current_votes, len(agents)):
            winner = max(current_votes, key=current_votes.get)
            return JuryVerdict(
                verdict=winner,
                final_vote_counts=current_votes,
                rounds_taken=0,
                consensus_reached=True,
                vote_trajectory=vote_trajectory,
                key_arguments=[],
                holdouts=[]
            )
        
        # Multi-round deliberation
        for round_num in range(1, self.max_rounds + 1):
            print(f"\n[Jury Deliberation] Round {round_num}")
            
            # Discussion phase
            arguments = self._discussion_round(
                agents,
                current_votes,
                case_summary,
                round_num
            )
            key_arguments.extend(arguments)
            
            # Re-vote after discussion
            new_votes = self._revote(agents, arguments, verdict_options)
            vote_trajectory.append(new_votes)
            
            # Update positions
            for agent in agents:
                for response in self.state.responses[-len(agents):]:  # Last batch of responses
                    if response.agent_id == agent.name and response.vote:
                        agent_positions[agent.name] = response.vote
                        break
            
            # Check for consensus
            if self._check_consensus(new_votes, len(agents)):
                winner = max(new_votes, key=new_votes.get)
                holdouts = self._find_holdouts(vote_trajectory)
                
                return JuryVerdict(
                    verdict=winner,
                    final_vote_counts=new_votes,
                    rounds_taken=round_num,
                    consensus_reached=True,
                    vote_trajectory=vote_trajectory,
                    key_arguments=key_arguments[:5],  # Top 5 arguments
                    holdouts=holdouts
                )
            
            current_votes = new_votes
        
        # Hung jury if no consensus after max rounds
        if self.allow_hung_jury:
            holdouts = self._find_holdouts(vote_trajectory)
            return JuryVerdict(
                verdict="Hung Jury",
                final_vote_counts=current_votes,
                rounds_taken=self.max_rounds,
                consensus_reached=False,
                vote_trajectory=vote_trajectory,
                key_arguments=key_arguments[:5],
                holdouts=holdouts
            )
        else:
            # Force plurality verdict
            winner = max(current_votes, key=current_votes.get)
            return JuryVerdict(
                verdict=winner,
                final_vote_counts=current_votes,
                rounds_taken=self.max_rounds,
                consensus_reached=False,
                vote_trajectory=vote_trajectory,
                key_arguments=key_arguments[:5],
                holdouts=self._find_holdouts(vote_trajectory)
            )
    
    def _initial_vote(
        self,
        agents: List[Any],
        case_summary: str,
        evidence: List[str],
        charges: str,
        options: List[str]
    ) -> Dict[str, int]:
        """Collect initial secret votes from all jurors."""
        
        evidence_str = "\n".join([f"- {e}" for e in evidence]) if evidence else "See case summary"
        
        prompt = f"""You are a juror in a criminal trial.

CHARGES: {charges}

CASE SUMMARY:
{case_summary}

EVIDENCE:
{evidence_str}

As a juror, you must vote based on the evidence presented. 
Respond with ONLY your initial vote and brief reasoning:

VOTE: [Guilty or Not Guilty]
REASON: [1-2 sentences explaining your reasoning]
"""
        
        votes = Counter()
        
        for agent in agents:
            response = agent.think(prompt, context="Jury initial vote")
            
            # Parse vote
            vote = self._parse_jury_vote(response, options)
            votes[vote] += 1
            
            # Log
            self.log_response(
                agent_id=agent.name,
                response=response,
                vote=vote
            )
        
        return dict(votes)
    
    def _discussion_round(
        self,
        agents: List[Any],
        current_votes: Dict[str, int],
        case_summary: str,
        round_num: int
    ) -> List[str]:
        """Conduct a round of discussion where agents share arguments."""
        
        arguments = []
        
        # Share current vote distribution (anonymously)
        vote_summary = ", ".join([f"{count} vote(s) for {verdict}" 
                                  for verdict, count in current_votes.items()])
        
        prompt = f"""You are in jury deliberations (Round {round_num}).

CURRENT VOTE COUNT: {vote_summary}

The jury is not unanimous. Please share your strongest argument for your position.
Be persuasive but respectful. Consider the evidence and the burden of proof.

Your argument (2-3 sentences):"""
        
        # Each agent shares their argument
        for agent in agents:
            argument = agent.think(prompt, context="Jury deliberation argument")
            arguments.append(f"{agent.name}: {argument}")
            
            self.log_message(
                sender_id=agent.name,
                content=argument,
                message_type="argument"
            )
        
        return arguments
    
    def _revote(
        self,
        agents: List[Any],
        arguments: List[str],
        options: List[str]
    ) -> Dict[str, int]:
        """Re-vote after hearing arguments."""
        
        # Compile arguments from this round
        recent_arguments = "\n\n".join(arguments[-len(agents):])
        
        prompt = f"""The jury has heard the following arguments:

{recent_arguments}

After hearing these perspectives, has your position changed?
Consider if the arguments were persuasive and if reasonable doubt exists.

VOTE: [Guilty or Not Guilty]
BRIEF NOTE: [Did you change your mind? Why/why not?]"""
        
        votes = Counter()
        
        for agent in agents:
            response = agent.think(prompt, context="Jury re-vote")
            vote = self._parse_jury_vote(response, options)
            votes[vote] += 1
            
            self.log_response(
                agent_id=agent.name,
                response=response,
                vote=vote
            )
        
        return dict(votes)
    
    def _parse_jury_vote(self, response: str, options: List[str]) -> str:
        """Parse jury vote from response."""
        response_upper = response.upper()
        
        # Look for explicit vote
        if "VOTE:" in response_upper:
            vote_line = [line for line in response.split("\n") if "VOTE:" in line.upper()][0]
            vote_text = vote_line.split(":", 1)[1].strip()
            
            if "GUILTY" in vote_text.upper() and "NOT" not in vote_text.upper():
                return "Guilty"
            elif "NOT GUILTY" in vote_text.upper():
                return "Not Guilty"
        
        # Fallback: search entire response
        if "NOT GUILTY" in response_upper:
            return "Not Guilty"
        elif "GUILTY" in response_upper:
            return "Guilty"
        
        # Default to first option if unclear
        return options[0]
    
    def _check_consensus(self, votes: Dict[str, int], total_jurors: int) -> bool:
        """Check if consensus threshold is met."""
        if not votes:
            return False
        
        max_votes = max(votes.values())
        return (max_votes / total_jurors) >= self.required_consensus
    
    def _find_holdouts(self, vote_trajectory: List[Dict[str, int]]) -> List[str]:
        """Identify agents who never changed their vote."""
        # This is a simplified version - in full implementation,
        # we'd track individual agent votes across rounds
        return []


def simulate_trial(
    agents: List[Any],
    case_summary: str,
    charges: str,
    evidence: List[str],
    max_rounds: int = 3
) -> JuryVerdict:
    """
    Convenience function to simulate a jury trial.
    
    Example:
        verdict = simulate_trial(
            agents=jury_pool,
            case_summary="Defendant accused of theft...",
            charges="Grand Theft Auto",
            evidence=["Security footage", "Witness testimony"],
            max_rounds=3
        )
    """
    protocol = JuryProtocol(max_rounds=max_rounds)
    return protocol.execute(
        agents=agents,
        context={
            "case_summary": case_summary,
            "charges": charges,
            "evidence": evidence,
            "verdict_options": ["Guilty", "Not Guilty"]
        }
    )