# src/simulacrum/utils/exceptions.py
from typing import List, Optional


class SimulacrumError(Exception):
    """Base exception for simulacrum-ai."""
    pass


class CalibrationError(SimulacrumError):
    """Raised when calibration fails or data is insufficient."""
    pass


class InsufficientDataError(SimulacrumError):
    """Raised when there is not enough data to proceed."""

    def __init__(
        self,
        message: str,
        missing_fields: Optional[List[str]] = None,
        suggestions: Optional[List[str]] = None,
    ):
        super().__init__(message)
        self.missing_fields = missing_fields or []
        self.suggestions = suggestions or []


class GovernanceViolationError(SimulacrumError):
    """Raised when a governance policy is violated."""
    pass
