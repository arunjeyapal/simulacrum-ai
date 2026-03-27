# src/simulacrum/digital_twin/factory.py
from typing import Any, Dict, List, Optional

from ..agents.persona import PsychologicalProfile
from .twin import DigitalTwin
from .team import TeamDigitalTwin


def quick_twin(
    openness: float = 0.5,
    conscientiousness: float = 0.5,
    extraversion: float = 0.5,
    agreeableness: float = 0.5,
    neuroticism: float = 0.5,
    name: str = "Twin",
) -> DigitalTwin:
    """
    Create a DigitalTwin directly from Big Five trait values.

    Args:
        openness: Openness to experience (0.0–1.0)
        conscientiousness: Conscientiousness (0.0–1.0)
        extraversion: Extraversion (0.0–1.0)
        agreeableness: Agreeableness (0.0–1.0)
        neuroticism: Neuroticism (0.0–1.0)
        name: Name for the twin

    Returns:
        DigitalTwin instance ready for simulation
    """
    traits = PsychologicalProfile(
        openness=openness,
        conscientiousness=conscientiousness,
        extraversion=extraversion,
        agreeableness=agreeableness,
        neuroticism=neuroticism,
    )
    twin = DigitalTwin(name=name, traits=traits)
    twin._calibration_score = 0.5  # Manual specification = moderate confidence
    return twin


def create_twin_from_survey(
    survey_responses: Dict[str, Any],
    name: Optional[str] = None,
    **kwargs: Any,
) -> DigitalTwin:
    """
    Create a DigitalTwin from survey responses.

    Delegates to DigitalTwin.from_survey for full calibration.
    """
    return DigitalTwin.from_survey(survey_responses, name=name, **kwargs)


def create_twin_from_behavior(
    behavioral_history: List[Dict],
    name: Optional[str] = None,
    **kwargs: Any,
) -> DigitalTwin:
    """
    Create a DigitalTwin from observed behavioral data.

    Delegates to DigitalTwin.from_behavioral_data.
    """
    return DigitalTwin.from_behavioral_data(behavioral_history, name=name, **kwargs)


def create_team_twin(
    members: List[DigitalTwin],
    name: str = "Team",
) -> "TeamDigitalTwin":
    """
    Create a TeamDigitalTwin from a list of individual DigitalTwin instances.
    """
    return TeamDigitalTwin(members=members, name=name)
