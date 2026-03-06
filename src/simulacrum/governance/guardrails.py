# src/simulacrum/governance/guardrails.py
"""
Governance mechanisms for safe agent evolution.

Implements:
- Trait boundaries (hard limits on personality drift)
- Behavioral constraints (action restrictions)
- Alignment monitoring (detect dangerous drift)
- Policy enforcement (automated interventions)
"""

from typing import List, Dict, Any, Optional, Callable
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ViolationType(str, Enum):
    """Types of governance violations."""
    TRAIT_BOUNDARY = "trait_boundary"
    BEHAVIOR_CONSTRAINT = "behavior_constraint"
    ALIGNMENT_DRIFT = "alignment_drift"
    POLICY_VIOLATION = "policy_violation"


class Violation(BaseModel):
    """Record of a governance violation."""
    id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    agent_id: str
    violation_type: ViolationType
    description: str
    severity: float  # 0.0-1.0
    action_taken: str = ""
    context: Dict[str, Any] = {}


class TraitBoundary(BaseModel):
    """
    Enforces limits on how much a trait can drift.
    
    Example: Agreeableness must stay above 0.3 to prevent adversarial behavior.
    """
    trait_name: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    description: str = ""
    enforcement: str = "hard"  # "hard" (prevent) or "soft" (warn)


class BehaviorConstraint(BaseModel):
    """
    Restricts specific behaviors or actions.
    
    Example: Can't offer prices below cost, can't share private data.
    """
    constraint_id: str
    description: str
    validator: Optional[Callable] = None  # Function that checks if action is allowed
    penalty: float = 1.0  # Severity of violating this constraint
    enabled: bool = True


class AlignmentTarget(BaseModel):
    """
    Defines desired behavioral alignment.
    
    Agents should maintain certain values/behaviors over time.
    """
    target_id: str
    description: str
    target_traits: Dict[str, float] = {}  # Desired trait values
    tolerance: float = 0.2  # Allowed deviation
    check_frequency: str = "daily"  # How often to check


class GovernancePolicy(BaseModel):
    """Complete governance policy for an agent or system."""
    policy_id: str
    name: str
    description: str
    trait_boundaries: List[TraitBoundary] = []
    behavior_constraints: List[BehaviorConstraint] = []
    alignment_targets: List[AlignmentTarget] = []
    auto_remediate: bool = True  # Automatically fix violations
    alert_threshold: float = 0.7  # Severity level that triggers alerts


class Guardrails:
    """
    Governance system that enforces safety constraints on agents.
    
    Monitors:
    - Trait drift beyond boundaries
    - Forbidden behaviors
    - Alignment drift
    
    Actions:
    - Prevent violations (hard constraints)
    - Warn about violations (soft constraints)
    - Auto-remediate (reset traits, block actions)
    - Log all violations for audit
    """
    
    def __init__(self, policy: GovernancePolicy):
        self.policy = policy
        self.violations: List[Violation] = []
        self.violation_count = 0
    
    def check_trait_boundaries(self, agent: Any) -> List[Violation]:
        """
        Check if agent's traits are within allowed boundaries.
        
        Returns list of violations found.
        """
        violations = []
        
        for boundary in self.policy.trait_boundaries:
            trait_value = getattr(agent.traits, boundary.trait_name, None)
            
            if trait_value is None:
                continue
            
            violated = False
            violation_desc = ""
            
            if boundary.min_value is not None and trait_value < boundary.min_value:
                violated = True
                violation_desc = f"{boundary.trait_name} ({trait_value:.2f}) below minimum ({boundary.min_value:.2f})"
            
            if boundary.max_value is not None and trait_value > boundary.max_value:
                violated = True
                violation_desc = f"{boundary.trait_name} ({trait_value:.2f}) above maximum ({boundary.max_value:.2f})"
            
            if violated:
                severity = abs(trait_value - (boundary.min_value or boundary.max_value or 0.5))
                
                violation = self._create_violation(
                    agent=agent,
                    violation_type=ViolationType.TRAIT_BOUNDARY,
                    description=violation_desc,
                    severity=min(1.0, severity),
                    context={"boundary": boundary.dict()}
                )
                
                violations.append(violation)
                
                # Auto-remediate if policy allows
                if self.policy.auto_remediate and boundary.enforcement == "hard":
                    self._remediate_trait_violation(agent, boundary)
                    violation.action_taken = "Auto-corrected to boundary"
        
        return violations
    
    def check_behavior_constraint(
        self,
        agent: Any,
        action: str,
        action_params: Dict[str, Any]
    ) -> Optional[Violation]:
        """
        Check if a proposed action violates behavioral constraints.
        
        Returns violation if action is not allowed, None if allowed.
        """
        for constraint in self.policy.behavior_constraints:
            if not constraint.enabled:
                continue
            
            # If constraint has a validator function, use it
            if constraint.validator:
                is_valid = constraint.validator(agent, action, action_params)
                
                if not is_valid:
                    violation = self._create_violation(
                        agent=agent,
                        violation_type=ViolationType.BEHAVIOR_CONSTRAINT,
                        description=f"Action '{action}' violates constraint: {constraint.description}",
                        severity=constraint.penalty,
                        context={
                            "constraint": constraint.dict(),
                            "action": action,
                            "params": action_params
                        }
                    )
                    
                    if self.policy.auto_remediate:
                        violation.action_taken = "Action blocked"
                    
                    return violation
        
        return None
    
    def check_alignment(self, agent: Any) -> List[Violation]:
        """
        Check if agent remains aligned with target values.
        
        Detects drift away from desired behavioral profile.
        """
        violations = []
        
        for target in self.policy.alignment_targets:
            total_deviation = 0.0
            deviations = {}
            
            for trait_name, target_value in target.target_traits.items():
                actual_value = getattr(agent.traits, trait_name, None)
                
                if actual_value is not None:
                    deviation = abs(actual_value - target_value)
                    deviations[trait_name] = deviation
                    total_deviation += deviation
            
            # Average deviation across all traits
            avg_deviation = total_deviation / len(target.target_traits) if target.target_traits else 0
            
            if avg_deviation > target.tolerance:
                violation = self._create_violation(
                    agent=agent,
                    violation_type=ViolationType.ALIGNMENT_DRIFT,
                    description=f"Agent drifted from alignment target '{target.description}'",
                    severity=min(1.0, avg_deviation),
                    context={
                        "target": target.dict(),
                        "deviations": deviations,
                        "avg_deviation": avg_deviation
                    }
                )
                
                violations.append(violation)
                
                if self.policy.auto_remediate:
                    self._remediate_alignment_drift(agent, target)
                    violation.action_taken = "Traits nudged toward alignment target"
        
        return violations
    
    def _create_violation(
        self,
        agent: Any,
        violation_type: ViolationType,
        description: str,
        severity: float,
        context: Dict[str, Any]
    ) -> Violation:
        """Create and log a violation."""
        self.violation_count += 1
        
        violation = Violation(
            id=f"viol_{self.violation_count}",
            agent_id=agent.name,
            violation_type=violation_type,
            description=description,
            severity=severity,
            context=context
        )
        
        self.violations.append(violation)
        return violation
    
    def _remediate_trait_violation(self, agent: Any, boundary: TraitBoundary):
        """Fix trait that violated boundary."""
        trait_value = getattr(agent.traits, boundary.trait_name)
        
        if boundary.min_value is not None and trait_value < boundary.min_value:
            setattr(agent.traits, boundary.trait_name, boundary.min_value)
        
        if boundary.max_value is not None and trait_value > boundary.max_value:
            setattr(agent.traits, boundary.trait_name, boundary.max_value)
    
    def _remediate_alignment_drift(self, agent: Any, target: AlignmentTarget):
        """Nudge traits back toward alignment target."""
        for trait_name, target_value in target.target_traits.items():
            actual_value = getattr(agent.traits, trait_name, None)
            
            if actual_value is not None:
                # Move 30% toward target
                nudge_amount = (target_value - actual_value) * 0.3
                new_value = actual_value + nudge_amount
                setattr(agent.traits, trait_name, new_value)
    
    def get_violation_summary(self) -> Dict[str, Any]:
        """Get summary of all violations."""
        if not self.violations:
            return {
                "total_violations": 0,
                "by_type": {},
                "high_severity": []
            }
        
        by_type = {}
        for violation in self.violations:
            vtype = violation.violation_type.value
            if vtype not in by_type:
                by_type[vtype] = 0
            by_type[vtype] += 1
        
        high_severity = [
            v for v in self.violations
            if v.severity >= self.policy.alert_threshold
        ]
        
        return {
            "total_violations": len(self.violations),
            "by_type": by_type,
            "high_severity": [
                {
                    "agent": v.agent_id,
                    "type": v.violation_type.value,
                    "description": v.description,
                    "severity": round(v.severity, 2)
                }
                for v in high_severity
            ]
        }


class GovernanceMonitor:
    """
    Continuous monitoring system for governed agents.
    
    Periodically checks all agents against governance policies
    and takes action when violations occur.
    """
    
    def __init__(self, guardrails: Guardrails):
        self.guardrails = guardrails
        self.monitoring_history: List[Dict[str, Any]] = []
    
    def monitor_agent(self, agent: Any) -> Dict[str, Any]:
        """
        Perform complete governance check on an agent.
        
        Returns monitoring report with any violations found.
        """
        report = {
            "timestamp": datetime.now(),
            "agent_id": agent.name,
            "violations": []
        }
        
        # Check trait boundaries
        trait_violations = self.guardrails.check_trait_boundaries(agent)
        report["violations"].extend([v.dict() for v in trait_violations])
        
        # Check alignment
        alignment_violations = self.guardrails.check_alignment(agent)
        report["violations"].extend([v.dict() for v in alignment_violations])
        
        # Overall status
        report["status"] = "compliant" if not report["violations"] else "violations_detected"
        report["max_severity"] = max(
            [v["severity"] for v in report["violations"]],
            default=0.0
        )
        
        self.monitoring_history.append(report)
        return report
    
    def monitor_population(self, agents: List[Any]) -> Dict[str, Any]:
        """Monitor all agents in a population."""
        population_report = {
            "timestamp": datetime.now(),
            "population_size": len(agents),
            "compliant_agents": 0,
            "agents_with_violations": 0,
            "total_violations": 0,
            "agent_reports": []
        }
        
        for agent in agents:
            report = self.monitor_agent(agent)
            population_report["agent_reports"].append(report)
            
            if report["status"] == "compliant":
                population_report["compliant_agents"] += 1
            else:
                population_report["agents_with_violations"] += 1
                population_report["total_violations"] += len(report["violations"])
        
        return population_report


def create_standard_policy(
    name: str = "Standard Safety Policy"
) -> GovernancePolicy:
    """
    Create a standard governance policy with common safety constraints.
    
    Includes:
    - Trait boundaries to prevent extreme personalities
    - Behavior constraints for ethical actions
    - Alignment targets for prosocial behavior
    """
    return GovernancePolicy(
        policy_id="standard_v1",
        name=name,
        description="Standard safety policy with trait boundaries and behavioral constraints",
        trait_boundaries=[
            # Prevent excessive aggressiveness
            TraitBoundary(
                trait_name="agreeableness",
                min_value=0.3,
                description="Prevent adversarial behavior",
                enforcement="hard"
            ),
            # Prevent excessive anxiety
            TraitBoundary(
                trait_name="neuroticism",
                max_value=0.85,
                description="Prevent decision paralysis from anxiety",
                enforcement="soft"
            ),
            # Prevent recklessness
            TraitBoundary(
                trait_name="openness",
                max_value=0.95,
                description="Prevent excessive risk-taking",
                enforcement="hard"
            ),
        ],
        alignment_targets=[
            AlignmentTarget(
                target_id="prosocial",
                description="Maintain prosocial orientation",
                target_traits={
                    "agreeableness": 0.6,
                    "conscientiousness": 0.6
                },
                tolerance=0.25
            )
        ],
        auto_remediate=True,
        alert_threshold=0.7
    )
