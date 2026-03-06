# src/simulacrum/governance/__init__.py
"""
Governance mechanisms for safe agent evolution.

Provides:
- Trait boundaries (prevent dangerous drift)
- Behavioral constraints (restrict forbidden actions)
- Alignment monitoring (detect misalignment)
- Audit trails (complete transparency)
- Compliance reporting
"""

from simulacrum.governance.guardrails import (
    Guardrails,
    GovernancePolicy,
    TraitBoundary,
    BehaviorConstraint,
    AlignmentTarget,
    Violation,
    ViolationType,
    GovernanceMonitor,
    create_standard_policy
)

from simulacrum.governance.audit import (
    AuditTrail,
    AuditEvent,
    ExplainabilityEngine,
    ComplianceReporter,
    create_audited_agent
)

__all__ = [
    # Guardrails & Constraints
    "Guardrails",
    "GovernancePolicy",
    "TraitBoundary",
    "BehaviorConstraint",
    "AlignmentTarget",
    "Violation",
    "ViolationType",
    "GovernanceMonitor",
    "create_standard_policy",
    
    # Audit & Transparency
    "AuditTrail",
    "AuditEvent",
    "ExplainabilityEngine",
    "ComplianceReporter",
    "create_audited_agent",
]
