# src/simulacrum/governance/explainability.py
"""
Re-exports ExplainabilityEngine from the audit module for backwards compatibility.
Also provides a DigitalTwin-aware explain_decision wrapper.
"""

from .audit import ExplainabilityEngine

__all__ = ["ExplainabilityEngine"]
