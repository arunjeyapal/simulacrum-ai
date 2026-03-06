# src/simulacrum/governance/audit.py
"""
Audit trail and transparency mechanisms for governance.

Provides:
- Complete decision history
- Trait evolution tracking
- Violation logs
- Explainability for agent actions
- Compliance reporting
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import json


class AuditEvent(BaseModel):
    """A single event in the audit trail."""
    id: str
    timestamp: datetime
    agent_id: str
    event_type: str  # decision, trait_change, violation, remediation
    description: str
    data: Dict[str, Any] = {}


class AuditTrail:
    """
    Complete audit trail for an agent or system.
    
    Tracks:
    - Every decision made
    - Every trait change
    - Every violation
    - Every remediation action
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.events: List[AuditEvent] = []
        self.event_count = 0
    
    def log_decision(
        self,
        decision: str,
        reasoning: str,
        outcome: Optional[str] = None,
        metadata: Dict[str, Any] = {}
    ):
        """Log a decision made by the agent."""
        self.event_count += 1
        
        event = AuditEvent(
            id=f"evt_{self.event_count}",
            timestamp=datetime.now(),
            agent_id=self.agent_id,
            event_type="decision",
            description=f"Decision: {decision}",
            data={
                "decision": decision,
                "reasoning": reasoning,
                "outcome": outcome,
                **metadata
            }
        )
        
        self.events.append(event)
    
    def log_trait_change(
        self,
        trait_name: str,
        old_value: float,
        new_value: float,
        cause: str = "experience"
    ):
        """Log a change in agent's personality traits."""
        self.event_count += 1
        
        event = AuditEvent(
            id=f"evt_{self.event_count}",
            timestamp=datetime.now(),
            agent_id=self.agent_id,
            event_type="trait_change",
            description=f"{trait_name} changed from {old_value:.2f} to {new_value:.2f}",
            data={
                "trait": trait_name,
                "old_value": old_value,
                "new_value": new_value,
                "delta": new_value - old_value,
                "cause": cause
            }
        )
        
        self.events.append(event)
    
    def log_violation(
        self,
        violation_type: str,
        description: str,
        severity: float,
        action_taken: str = ""
    ):
        """Log a governance violation."""
        self.event_count += 1
        
        event = AuditEvent(
            id=f"evt_{self.event_count}",
            timestamp=datetime.now(),
            agent_id=self.agent_id,
            event_type="violation",
            description=description,
            data={
                "violation_type": violation_type,
                "severity": severity,
                "action_taken": action_taken
            }
        )
        
        self.events.append(event)
    
    def log_remediation(
        self,
        what_was_fixed: str,
        how_fixed: str,
        metadata: Dict[str, Any] = {}
    ):
        """Log a remediation action."""
        self.event_count += 1
        
        event = AuditEvent(
            id=f"evt_{self.event_count}",
            timestamp=datetime.now(),
            agent_id=self.agent_id,
            event_type="remediation",
            description=f"Remediation: {what_was_fixed}",
            data={
                "what": what_was_fixed,
                "how": how_fixed,
                **metadata
            }
        )
        
        self.events.append(event)
    
    def get_events(
        self,
        event_type: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[AuditEvent]:
        """Retrieve events from audit trail with filters."""
        events = self.events
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if since:
            events = [e for e in events if e.timestamp >= since]
        
        if limit:
            events = events[-limit:]
        
        return events
    
    def export_to_json(self, filepath: str):
        """Export audit trail to JSON file."""
        data = {
            "agent_id": self.agent_id,
            "total_events": len(self.events),
            "events": [e.dict() for e in self.events]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def generate_report(
        self,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Generate compliance report for a time period."""
        cutoff = datetime.now() - timedelta(days=period_days)
        recent_events = [e for e in self.events if e.timestamp >= cutoff]
        
        report = {
            "agent_id": self.agent_id,
            "period_days": period_days,
            "total_events": len(recent_events),
            "events_by_type": {},
            "violations": 0,
            "remediations": 0,
            "trait_changes": []
        }
        
        for event in recent_events:
            # Count by type
            etype = event.event_type
            if etype not in report["events_by_type"]:
                report["events_by_type"][etype] = 0
            report["events_by_type"][etype] += 1
            
            # Track violations
            if etype == "violation":
                report["violations"] += 1
            
            # Track remediations
            if etype == "remediation":
                report["remediations"] += 1
            
            # Track trait changes
            if etype == "trait_change":
                report["trait_changes"].append({
                    "trait": event.data.get("trait"),
                    "delta": event.data.get("delta"),
                    "timestamp": event.timestamp
                })
        
        return report


class ExplainabilityEngine:
    """
    Explains agent decisions and behaviors.
    
    Provides transparency into:
    - Why agent made a decision
    - What influenced their thinking
    - How their personality shaped the choice
    """
    
    def __init__(self, agent: Any):
        self.agent = agent
    
    def explain_decision(
        self,
        decision: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate natural language explanation of a decision.
        
        Includes:
        - The decision itself
        - Personality traits that influenced it
        - Relevant experiences
        - Learned strategies applied
        """
        explanation = f"Agent '{self.agent.name}' chose: {decision}\n\n"
        
        # Personality influence
        explanation += "Personality factors:\n"
        traits = self.agent.traits
        
        if traits.openness > 0.7:
            explanation += f"- High openness ({traits.openness:.2f}): Willing to try innovative approaches\n"
        elif traits.openness < 0.3:
            explanation += f"- Low openness ({traits.openness:.2f}): Prefers proven, traditional methods\n"
        
        if traits.conscientiousness > 0.7:
            explanation += f"- High conscientiousness ({traits.conscientiousness:.2f}): Careful, thorough evaluation\n"
        
        if traits.neuroticism > 0.7:
            explanation += f"- High neuroticism ({traits.neuroticism:.2f}): Risk-averse, cautious approach\n"
        
        if traits.agreeableness > 0.7:
            explanation += f"- High agreeableness ({traits.agreeableness:.2f}): Considers others' perspectives\n"
        
        # Recent experiences
        if hasattr(self.agent, 'experiences'):
            recent = self.agent.experiences[-3:] if self.agent.experiences else []
            if recent:
                explanation += "\nRecent experiences:\n"
                for exp in recent:
                    explanation += f"- {exp.description} ({exp.type.value})\n"
        
        # Learned strategies
        if hasattr(self.agent, 'strategies'):
            relevant = [
                s for s in self.agent.strategies.values()
                if s.success_rate > 0.6 and s.times_used > 2
            ]
            if relevant:
                explanation += "\nSuccessful strategies applied:\n"
                for strategy in relevant[:3]:
                    explanation += f"- {strategy.description} (success rate: {strategy.success_rate:.1%})\n"
        
        return explanation
    
    def explain_trait_evolution(
        self,
        trait_name: str,
        audit_trail: AuditTrail
    ) -> str:
        """
        Explain how and why a trait evolved.
        
        Traces history of changes and their causes.
        """
        trait_events = [
            e for e in audit_trail.events
            if e.event_type == "trait_change" and e.data.get("trait") == trait_name
        ]
        
        if not trait_events:
            return f"No changes recorded for {trait_name}"
        
        current_value = getattr(self.agent.traits, trait_name)
        initial_value = trait_events[0].data.get("old_value", current_value)
        total_change = current_value - initial_value
        
        explanation = f"Evolution of {trait_name}:\n"
        explanation += f"Initial value: {initial_value:.2f}\n"
        explanation += f"Current value: {current_value:.2f}\n"
        explanation += f"Total change: {total_change:+.2f}\n\n"
        
        explanation += "Key changes:\n"
        for event in trait_events[-5:]:  # Last 5 changes
            delta = event.data.get("delta", 0)
            cause = event.data.get("cause", "unknown")
            explanation += f"- {delta:+.2f} due to {cause}\n"
        
        return explanation


class ComplianceReporter:
    """
    Generates compliance reports for governance oversight.
    
    Produces:
    - Agent compliance summaries
    - Population health metrics
    - Violation trend analysis
    - Risk assessments
    """
    
    def __init__(self):
        self.reports_generated = 0
    
    def generate_agent_report(
        self,
        agent: Any,
        audit_trail: AuditTrail,
        guardrails: Any
    ) -> Dict[str, Any]:
        """Generate compliance report for a single agent."""
        violations = [
            e for e in audit_trail.events
            if e.event_type == "violation"
        ]
        
        recent_violations = [
            v for v in violations
            if (datetime.now() - v.timestamp).days <= 30
        ]
        
        report = {
            "agent_id": agent.name,
            "report_date": datetime.now(),
            "current_traits": {
                "openness": agent.traits.openness,
                "conscientiousness": agent.traits.conscientiousness,
                "extraversion": agent.traits.extraversion,
                "agreeableness": agent.traits.agreeableness,
                "neuroticism": agent.traits.neuroticism
            },
            "total_violations": len(violations),
            "violations_last_30_days": len(recent_violations),
            "compliance_status": "compliant" if len(recent_violations) == 0 else "requires_attention",
            "risk_level": self._assess_risk(agent, recent_violations)
        }
        
        return report
    
    def generate_population_report(
        self,
        agents: List[Any],
        audit_trails: Dict[str, AuditTrail],
        guardrails: Any
    ) -> Dict[str, Any]:
        """Generate compliance report for entire population."""
        total_violations = 0
        high_risk_agents = []
        
        agent_reports = []
        for agent in agents:
            if agent.name in audit_trails:
                agent_report = self.generate_agent_report(
                    agent,
                    audit_trails[agent.name],
                    guardrails
                )
                agent_reports.append(agent_report)
                total_violations += agent_report["total_violations"]
                
                if agent_report["risk_level"] == "high":
                    high_risk_agents.append(agent.name)
        
        return {
            "report_date": datetime.now(),
            "population_size": len(agents),
            "total_violations": total_violations,
            "avg_violations_per_agent": total_violations / len(agents) if agents else 0,
            "compliant_agents": len([r for r in agent_reports if r["compliance_status"] == "compliant"]),
            "high_risk_agents": high_risk_agents,
            "population_health": "healthy" if len(high_risk_agents) == 0 else "needs_intervention"
        }
    
    def _assess_risk(
        self,
        agent: Any,
        recent_violations: List[AuditEvent]
    ) -> str:
        """Assess risk level of an agent."""
        if len(recent_violations) == 0:
            return "low"
        
        # Check severity
        high_severity = [
            v for v in recent_violations
            if v.data.get("severity", 0) > 0.7
        ]
        
        if len(high_severity) >= 3:
            return "high"
        elif len(recent_violations) >= 5:
            return "medium"
        else:
            return "low"


def create_audited_agent(
    base_agent: Any
) -> tuple[Any, AuditTrail]:
    """
    Wrap an agent with audit trail.
    
    Returns (agent, audit_trail) tuple.
    
    Example:
        agent, trail = create_audited_agent(my_agent)
        
        # Decisions are automatically logged
        agent.make_decision(...)
        
        # View audit history
        report = trail.generate_report(period_days=30)
    """
    audit_trail = AuditTrail(base_agent.name)
    return base_agent, audit_trail
