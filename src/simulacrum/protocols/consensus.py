# src/simulacrum/protocols/consensus.py
from typing import Any, Dict, List, Optional


def consensus_protocol(
    agents: List[Any],
    proposal: str,
    rounds: int = 3,
    threshold: float = 0.67,
) -> Dict[str, Any]:
    """
    Run a multi-round consensus protocol among agents.

    Args:
        agents: List of Citizen / agent objects with a .think() method.
        proposal: The proposal to reach consensus on.
        rounds: Number of deliberation rounds.
        threshold: Fraction of agents needed to accept (default 2/3).

    Returns:
        Dict with keys: consensus_reached, acceptance_rate, final_vote, responses.
    """
    responses: List[Dict[str, Any]] = []
    current_proposal = proposal

    for round_num in range(1, rounds + 1):
        round_votes: List[str] = []
        for agent in agents:
            if hasattr(agent, "think"):
                reply = agent.think(
                    f"Round {round_num} — Proposal: {current_proposal}\n"
                    "Do you accept? Reply with Accept or Decline and a brief reason."
                )
            else:
                reply = "Accept"
            round_votes.append(reply)

        accept_count = sum(
            1 for v in round_votes if "accept" in v.lower()
        )
        acceptance_rate = accept_count / len(agents) if agents else 0.0

        responses.append(
            {
                "round": round_num,
                "votes": round_votes,
                "acceptance_rate": acceptance_rate,
            }
        )

        if acceptance_rate >= threshold:
            return {
                "consensus_reached": True,
                "acceptance_rate": acceptance_rate,
                "final_vote": "Accept",
                "rounds_taken": round_num,
                "responses": responses,
            }

    return {
        "consensus_reached": False,
        "acceptance_rate": responses[-1]["acceptance_rate"] if responses else 0.0,
        "final_vote": "Decline",
        "rounds_taken": rounds,
        "responses": responses,
    }
