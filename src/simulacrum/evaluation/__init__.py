# src/simulacrum/evaluation/__init__.py
"""
Validation and evaluation framework for synthetic agents.

Provides:
- Statistical tests for each layer
- Reproducible experiments
- Confidence intervals
- Automated validation
"""

from simulacrum.evaluation.validators import (
    PsychologicalValidator,
    ProtocolValidator,
    EconomicValidator,
    TemporalValidator,
    GovernanceValidator,
    ValidationReport,
    TestResult,
    ValidationResult
)

__all__ = [
    # Validators
    "PsychologicalValidator",
    "ProtocolValidator",
    "EconomicValidator",
    "TemporalValidator",
    "GovernanceValidator",
    
    # Report
    "ValidationReport",
    
    # Results
    "TestResult",
    "ValidationResult",
]
