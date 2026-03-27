# src/simulacrum/digital_twin/ethics.py
"""
Ethics and Governance framework for responsible digital twin usage.

This module provides tools for consent management, privacy protection,
usage policies, and ethical oversight of digital twins.
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from ..utils.exceptions import GovernanceViolationError


class PermissionLevel(Enum):
    """Permission levels for digital twin operations."""
    NONE = "none"                      # No access
    READ_ONLY = "read_only"           # Can view but not simulate
    DECISION_SIMULATION = "decision"  # Can simulate decisions
    FULL_ACCESS = "full"              # All operations including export


class UsageContext(Enum):
    """Valid contexts for digital twin usage."""
    PERSONAL = "personal"             # Personal decision-making
    RESEARCH = "research"             # Academic research
    PRODUCT_TESTING = "product_test"  # Product/UX testing
    HR_SIMULATION = "hr"              # HR/hiring simulation
    TEAM_DYNAMICS = "team"            # Team collaboration
    COMMERCIAL = "commercial"         # Commercial applications


@dataclass
class EthicsPolicy:
    """
    Ethics policy for digital twin usage.
    
    Defines what is allowed and what safeguards are in place.
    
    Attributes:
        consent_required: Whether explicit consent is needed
        allowed_contexts: List of permitted usage contexts
        data_retention_days: How long to keep data (None = indefinite)
        third_party_access: Whether third parties can access
        anonymization_required: Whether to anonymize data
        audit_logging: Whether to log all operations
    """
    consent_required: bool = True
    allowed_contexts: List[UsageContext] = field(default_factory=lambda: [UsageContext.PERSONAL])
    data_retention_days: Optional[int] = None
    third_party_access: bool = False
    anonymization_required: bool = False
    audit_logging: bool = True
    
    def allows_context(self, context: UsageContext) -> bool:
        """Check if a usage context is allowed."""
        return context in self.allowed_contexts
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            "consent_required": self.consent_required,
            "allowed_contexts": [c.value for c in self.allowed_contexts],
            "data_retention_days": self.data_retention_days,
            "third_party_access": self.third_party_access,
            "anonymization_required": self.anonymization_required,
            "audit_logging": self.audit_logging
        }


@dataclass
class ConsentRecord:
    """
    Record of user consent for digital twin operations.
    
    Attributes:
        granted: Whether consent was granted
        permissions: Set of granted permissions
        context: Context in which consent was given
        timestamp: When consent was granted
        expiry: Optional expiration date
        revocable: Whether consent can be revoked
    """
    granted: bool
    permissions: Set[PermissionLevel]
    context: UsageContext
    timestamp: datetime = field(default_factory=datetime.now)
    expiry: Optional[datetime] = None
    revocable: bool = True
    
    def is_valid(self) -> bool:
        """Check if consent is still valid."""
        if not self.granted:
            return False
        
        if self.expiry and datetime.now() > self.expiry:
            return False
        
        return True
    
    def has_permission(self, permission: PermissionLevel) -> bool:
        """Check if specific permission is granted."""
        return self.is_valid() and permission in self.permissions
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            "granted": self.granted,
            "permissions": [p.value for p in self.permissions],
            "context": self.context.value,
            "timestamp": self.timestamp.isoformat(),
            "expiry": self.expiry.isoformat() if self.expiry else None,
            "revocable": self.revocable
        }


class ConsentManager:
    """
    Manages consent and permissions for digital twin operations.
    
    Tracks what operations are allowed, enforces consent requirements,
    and provides audit trail of permission usage.
    
    Examples:
        >>> consent = ConsentManager(twin)
        >>> 
        >>> # Grant permission
        >>> consent.grant_permission(
        ...     PermissionLevel.DECISION_SIMULATION,
        ...     context=UsageContext.PERSONAL
        ... )
        >>> 
        >>> # Check permission
        >>> if consent.check_permission(PermissionLevel.DECISION_SIMULATION):
        ...     decision = twin.simulate_decision(...)
        >>> 
        >>> # Revoke permission
        >>> consent.revoke_permission(PermissionLevel.DECISION_SIMULATION)
    """
    
    def __init__(self, twin_name: str, policy: Optional[EthicsPolicy] = None):
        """
        Initialize consent manager.
        
        Args:
            twin_name: Name of the digital twin
            policy: Optional ethics policy (uses default if None)
        """
        self.twin_name = twin_name
        self.policy = policy or EthicsPolicy()
        self._consent_records: List[ConsentRecord] = []
        self._audit_log: List[Dict] = []
    
    def grant_permission(
        self,
        permission: PermissionLevel,
        context: UsageContext,
        expiry: Optional[datetime] = None
    ) -> None:
        """
        Grant a specific permission.
        
        Args:
            permission: Permission level to grant
            context: Context in which permission applies
            expiry: Optional expiration date
            
        Examples:
            >>> consent.grant_permission(
            ...     PermissionLevel.DECISION_SIMULATION,
            ...     context=UsageContext.PERSONAL,
            ...     expiry=datetime.now() + timedelta(days=30)
            ... )
        """
        # Check if context is allowed by policy
        if not self.policy.allows_context(context):
            raise GovernanceViolationError(
                f"Context '{context.value}' not allowed by ethics policy. "
                f"Allowed contexts: {[c.value for c in self.policy.allowed_contexts]}"
            )
        
        # Create consent record
        record = ConsentRecord(
            granted=True,
            permissions={permission},
            context=context,
            expiry=expiry
        )
        
        self._consent_records.append(record)
        
        # Audit log
        self._log_action("grant_permission", {
            "permission": permission.value,
            "context": context.value,
            "expiry": expiry.isoformat() if expiry else None
        })
    
    def revoke_permission(
        self,
        permission: Optional[PermissionLevel] = None
    ) -> None:
        """
        Revoke permission(s).
        
        Args:
            permission: Specific permission to revoke, or None to revoke all
            
        Examples:
            >>> # Revoke specific permission
            >>> consent.revoke_permission(PermissionLevel.DECISION_SIMULATION)
            >>> 
            >>> # Revoke all permissions
            >>> consent.revoke_permission()
        """
        if permission is None:
            # Revoke all
            for record in self._consent_records:
                if record.revocable:
                    record.granted = False
            
            self._log_action("revoke_all_permissions", {})
        else:
            # Revoke specific
            for record in self._consent_records:
                if record.revocable and permission in record.permissions:
                    record.permissions.remove(permission)
                    if not record.permissions:
                        record.granted = False
            
            self._log_action("revoke_permission", {
                "permission": permission.value
            })
    
    def check_permission(
        self,
        permission: PermissionLevel,
        context: Optional[UsageContext] = None,
        raise_on_deny: bool = False
    ) -> bool:
        """
        Check if a permission is granted.
        
        Args:
            permission: Permission to check
            context: Optional specific context
            raise_on_deny: Whether to raise exception if denied
            
        Returns:
            True if permission granted, False otherwise
            
        Raises:
            GovernanceViolationError: If raise_on_deny=True and permission denied
            
        Examples:
            >>> if consent.check_permission(PermissionLevel.DECISION_SIMULATION):
            ...     # Permission granted
            ...     decision = twin.simulate_decision(...)
        """
        # Check if any valid consent record grants this permission
        for record in self._consent_records:
            if not record.is_valid():
                continue
            
            # Check context match if specified
            if context and record.context != context:
                continue
            
            if record.has_permission(permission):
                self._log_action("permission_check", {
                    "permission": permission.value,
                    "context": context.value if context else None,
                    "result": "granted"
                })
                return True
        
        # Permission not found
        self._log_action("permission_check", {
            "permission": permission.value,
            "context": context.value if context else None,
            "result": "denied"
        })
        
        if raise_on_deny:
            raise GovernanceViolationError(
                f"Permission '{permission.value}' not granted for digital twin '{self.twin_name}'. "
                f"Call grant_permission() first."
            )
        
        return False
    
    def get_active_permissions(self) -> Dict[PermissionLevel, List[UsageContext]]:
        """
        Get all currently active permissions.
        
        Returns:
            Dictionary mapping permissions to contexts where they're granted
            
        Examples:
            >>> perms = consent.get_active_permissions()
            >>> print(perms)
            {
                PermissionLevel.DECISION_SIMULATION: [UsageContext.PERSONAL],
                PermissionLevel.READ_ONLY: [UsageContext.RESEARCH]
            }
        """
        active: Dict[PermissionLevel, List[UsageContext]] = {}
        
        for record in self._consent_records:
            if record.is_valid():
                for perm in record.permissions:
                    if perm not in active:
                        active[perm] = []
                    if record.context not in active[perm]:
                        active[perm].append(record.context)
        
        return active
    
    def get_audit_log(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get audit log of permission operations.
        
        Args:
            limit: Optional limit on number of entries
            
        Returns:
            List of audit log entries
        """
        log = sorted(
            self._audit_log,
            key=lambda x: x["timestamp"],
            reverse=True
        )
        
        if limit:
            return log[:limit]
        return log
    
    def export_consent_status(self) -> Dict:
        """
        Export complete consent status for transparency.
        
        Returns:
            Dictionary with all consent information
        """
        return {
            "twin_name": self.twin_name,
            "policy": self.policy.to_dict(),
            "active_permissions": {
                k.value: [c.value for c in v]
                for k, v in self.get_active_permissions().items()
            },
            "consent_records": [r.to_dict() for r in self._consent_records],
            "audit_log_entries": len(self._audit_log)
        }
    
    def _log_action(self, action: str, details: Dict) -> None:
        """Log action to audit trail."""
        if self.policy.audit_logging:
            self._audit_log.append({
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "details": details,
                "twin_name": self.twin_name
            })


class DigitalTwinEthics:
    """
    Ethics framework for digital twin operations.
    
    Provides high-level ethical oversight, usage policies,
    and responsible AI practices for digital twins.
    
    Examples:
        >>> ethics = DigitalTwinEthics()
        >>> 
        >>> # Check if usage is ethical
        >>> if ethics.validate_usage(twin, context=UsageContext.RESEARCH):
        ...     decision = twin.simulate_decision(...)
        >>> 
        >>> # Get ethical guidelines
        >>> guidelines = ethics.get_guidelines(UsageContext.HR_SIMULATION)
    """
    
    def __init__(self, policy: Optional[EthicsPolicy] = None):
        """
        Initialize ethics framework.
        
        Args:
            policy: Optional custom ethics policy
        """
        self.policy = policy or EthicsPolicy()
        self._guidelines = self._build_guidelines()
    
    def validate_usage(
        self,
        twin_name: str,
        context: UsageContext,
        consent_manager: Optional[ConsentManager] = None
    ) -> bool:
        """
        Validate if a proposed usage is ethical.
        
        Args:
            twin_name: Name of digital twin
            context: Proposed usage context
            consent_manager: Optional consent manager to check
            
        Returns:
            True if usage is ethical, False otherwise
        """
        # Check if context is allowed by policy
        if not self.policy.allows_context(context):
            return False
        
        # Check consent if required
        if self.policy.consent_required and consent_manager:
            if not consent_manager.check_permission(PermissionLevel.DECISION_SIMULATION, context):
                return False
        
        return True
    
    def get_guidelines(self, context: UsageContext) -> List[str]:
        """
        Get ethical guidelines for a specific usage context.
        
        Args:
            context: Usage context
            
        Returns:
            List of guideline strings
        """
        return self._guidelines.get(context, self._guidelines[UsageContext.PERSONAL])
    
    def _build_guidelines(self) -> Dict[UsageContext, List[str]]:
        """Build ethical guidelines for each context."""
        return {
            UsageContext.PERSONAL: [
                "Use for your own decision-making and self-reflection",
                "Keep your digital twin data private and secure",
                "Regularly review and update your personality calibration",
                "Use insights to enhance, not replace, personal judgment"
            ],
            
            UsageContext.RESEARCH: [
                "Obtain informed consent from all participants",
                "Anonymize data when sharing research results",
                "Use digital twins to complement, not replace, human studies",
                "Clearly disclose use of digital twin simulations in publications",
                "Respect participant right to withdraw consent"
            ],
            
            UsageContext.PRODUCT_TESTING: [
                "Do not use digital twins to manipulate user behavior",
                "Ensure diverse representation in test population",
                "Use for understanding, not exploiting, user psychology",
                "Be transparent about use of behavioral simulation in products"
            ],
            
            UsageContext.HR_SIMULATION: [
                "Never use digital twins as sole basis for hiring decisions",
                "Ensure fairness and avoid discrimination",
                "Use only for understanding team dynamics, not evaluating individuals",
                "Obtain explicit consent before creating work-related digital twins",
                "Protect employee privacy and data"
            ],
            
            UsageContext.TEAM_DYNAMICS: [
                "Use to improve collaboration, not surveillance",
                "Respect individual autonomy and privacy",
                "Share insights with team transparently",
                "Use predictions as guidance, not mandates"
            ],
            
            UsageContext.COMMERCIAL: [
                "Obtain explicit consent for commercial use",
                "Compensate individuals whose digital twins are used commercially",
                "Ensure transparency about commercial applications",
                "Respect user rights and data ownership",
                "Comply with data protection regulations (GDPR, CCPA, etc.)"
            ]
        }


# Convenience functions

def create_consent_manager(
    twin_name: str,
    allow_personal: bool = True,
    allow_research: bool = False,
    allow_commercial: bool = False
) -> ConsentManager:
    """
    Create a consent manager with common settings.
    
    Args:
        twin_name: Name of digital twin
        allow_personal: Allow personal use
        allow_research: Allow research use
        allow_commercial: Allow commercial use
        
    Returns:
        Configured ConsentManager
        
    Examples:
        >>> # Personal use only
        >>> consent = create_consent_manager("Alice", allow_personal=True)
        >>> 
        >>> # Research use
        >>> consent = create_consent_manager(
        ...     "Study Participant",
        ...     allow_personal=True,
        ...     allow_research=True
        ... )
    """
    allowed_contexts = []
    
    if allow_personal:
        allowed_contexts.append(UsageContext.PERSONAL)
    if allow_research:
        allowed_contexts.append(UsageContext.RESEARCH)
    if allow_commercial:
        allowed_contexts.append(UsageContext.COMMERCIAL)
    
    policy = EthicsPolicy(
        consent_required=True,
        allowed_contexts=allowed_contexts,
        audit_logging=True
    )
    
    return ConsentManager(twin_name, policy)


def get_ethical_guidelines(context: UsageContext) -> List[str]:
    """
    Get ethical guidelines for a usage context.
    
    Args:
        context: Usage context
        
    Returns:
        List of guideline strings
        
    Examples:
        >>> guidelines = get_ethical_guidelines(UsageContext.RESEARCH)
        >>> for guideline in guidelines:
        ...     print(f"• {guideline}")
    """
    ethics = DigitalTwinEthics()
    return ethics.get_guidelines(context)
