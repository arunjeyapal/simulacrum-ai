# src/simulacrum/__init__.py
"""
Simulacrum: Production framework for behavioral AI agents and digital twins.

Quick Start:
    >>> from simulacrum import DigitalTwin
    >>> twin = DigitalTwin.from_survey(survey_responses)
    >>> decision = twin.simulate_decision("Should I take this job?")
    >>> print(decision.recommendation)

Installation:
    pip install simulacrum-ai

Documentation:
    https://simulacrum-ai.readthedocs.io

GitHub:
    https://github.com/arun-jayapal/simulacrum-ai
"""

# Version
from .__version__ import __version__, __version_info__

# Core: Individual psychology (Series 1, Article 1)
from .agents.persona import (
    PsychologicalProfile,
    Citizen,
    create_early_adopter,
    create_skeptic,
    create_analyst,
)

# Protocols: Collective intelligence (Series 1, Article 2)
from .protocols.voting import quick_vote
from .protocols.consensus import consensus_protocol
from .protocols.jury import simulate_trial as jury_deliberation

# Economy: Economic behavior (Series 1, Article 3)
from .economy.wallet import Wallet, create_economic_citizen
from .economy.negotiation import negotiate_price
from .economy.marketplace import Marketplace

# Evolution: Temporal dynamics (Series 1, Article 4)
from .evolution.temporal import create_temporal_agent, ExperienceType
from .evolution.learning import create_adaptive_learner, OutcomeType

# Governance: Safety & control (Series 1, Article 5)
from .governance.guardrails import Guardrails, GovernancePolicy, TraitBoundary
from .governance.audit import AuditTrail
from .governance.explainability import ExplainabilityEngine

# Validation: Testing & proof (Series 1, Articles 7-8)
from .evaluation.validators import (
    PsychologicalValidator,
    ProtocolValidator,
    EconomicValidator,
    TemporalValidator,
    GovernanceValidator,
)

# Digital Twin: Personalized replicas (Series 2, NEW)
from .digital_twin.twin import DigitalTwin
from .digital_twin.factory import (
    create_twin_from_survey,
    create_twin_from_behavior,
    create_team_twin,
    quick_twin,
)
from .digital_twin.calibration import PersonalityAssessment, BehavioralCalibrator
from .digital_twin.team import TeamDigitalTwin
from .digital_twin.ethics import DigitalTwinEthics, ConsentManager

# Configuration
from .utils.config import (
    configure,
    get_config,
    use_openai,
    use_gemini,
    use_anthropic,
    print_config,
    reset_config,
    is_configured,
)

# Exceptions
from .utils.exceptions import (
    SimulacrumError,
    CalibrationError,
    InsufficientDataError,
    GovernanceViolationError,
)

__all__ = [
    # Version
    "__version__",
    "__version_info__",
    # Core (Article 1)
    "PsychologicalProfile",
    "Citizen",
    "create_early_adopter",
    "create_skeptic",
    "create_analyst",
    # Protocols (Article 2)
    "quick_vote",
    "consensus_protocol",
    "jury_deliberation",
    # Economy (Article 3)
    "Wallet",
    "create_economic_citizen",
    "negotiate_price",
    "Marketplace",
    # Evolution (Article 4)
    "create_temporal_agent",
    "ExperienceType",
    "create_adaptive_learner",
    "OutcomeType",
    # Governance (Article 5)
    "Guardrails",
    "GovernancePolicy",
    "TraitBoundary",
    "AuditTrail",
    "ExplainabilityEngine",
    # Validation (Articles 7-8)
    "PsychologicalValidator",
    "ProtocolValidator",
    "EconomicValidator",
    "TemporalValidator",
    "GovernanceValidator",
    # Digital Twin (Series 2, NEW)
    "DigitalTwin",
    "create_twin_from_survey",
    "create_twin_from_behavior",
    "create_team_twin",
    "quick_twin",
    "PersonalityAssessment",
    "BehavioralCalibrator",
    "TeamDigitalTwin",
    "DigitalTwinEthics",
    "ConsentManager",
    # Configuration
    "configure",
    "get_config",
    "use_openai",
    "use_gemini",
    "use_anthropic",
    "print_config",
    "reset_config",
    "is_configured",
    # Exceptions
    "SimulacrumError",
    "CalibrationError",
    "InsufficientDataError",
    "GovernanceViolationError",
]

# Package metadata
__author__ = "Arun Jayapal"
__email__ = "contact@arunjayapal.com"
__license__ = "MIT"
__status__ = "Beta"
