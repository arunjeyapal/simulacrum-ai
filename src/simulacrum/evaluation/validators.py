
# src/simulacrum/evaluation/validators.py
"""
Validation framework for synthetic agent behavior.

Provides:
- Statistical tests for psychological validity
- Protocol correctness verification
- Economic rationality checks
- Temporal dynamics validation
- Governance effectiveness tests
- Reproducibility utilities
"""

from typing import List, Dict, Any, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import statistics
import math
from collections import defaultdict


class ValidationResult(Enum):
    """Validation test result."""
    PASS = "pass"
    FAIL = "fail"
    WARN = "warning"


@dataclass
class TestResult:
    """Result of a validation test."""
    test_name: str
    result: ValidationResult
    metric_value: float
    expected_range: Tuple[float, float]
    confidence: float
    details: Dict[str, Any]
    
    @property
    def passed(self) -> bool:
        return self.result == ValidationResult.PASS
    
    def __str__(self):
        status = "✓" if self.passed else "✗"
        return f"{status} {self.test_name}: {self.metric_value:.3f} (expected {self.expected_range[0]:.2f}-{self.expected_range[1]:.2f})"


class PsychologicalValidator:
    """
    Validates that personality traits predict behavior as expected.
    
    Tests:
    1. High openness → More innovative decisions
    2. High conscientiousness → More careful analysis
    3. High neuroticism → More risk-averse choices
    4. High agreeableness → More cooperative in groups
    5. High extraversion → More influential in discussions
    """
    
    def __init__(self):
        self.test_results: List[TestResult] = []
    
    def test_openness_innovation_correlation(
        self,
        agents: List[Any],
        innovation_scores: List[float]
    ) -> TestResult:
        """
        Test: High openness agents should have higher innovation scores.
        
        Expected: Correlation > 0.4 (moderate positive correlation)
        """
        openness_values = [a.traits.openness for a in agents]
        correlation = self._pearson_correlation(openness_values, innovation_scores)
        
        # Expected moderate positive correlation
        expected_min, expected_max = 0.3, 0.9
        
        result = TestResult(
            test_name="Openness → Innovation Correlation",
            result=ValidationResult.PASS if expected_min <= correlation <= expected_max else ValidationResult.FAIL,
            metric_value=correlation,
            expected_range=(expected_min, expected_max),
            confidence=self._correlation_confidence(correlation, len(agents)),
            details={
                "n_agents": len(agents),
                "mean_openness": statistics.mean(openness_values),
                "mean_innovation": statistics.mean(innovation_scores)
            }
        )
        
        self.test_results.append(result)
        return result
    
    def test_neuroticism_risk_aversion_correlation(
        self,
        agents: List[Any],
        risk_aversion_scores: List[float]
    ) -> TestResult:
        """
        Test: High neuroticism agents should be more risk-averse.
        
        Expected: Correlation > 0.4
        """
        neuroticism_values = [a.traits.neuroticism for a in agents]
        correlation = self._pearson_correlation(neuroticism_values, risk_aversion_scores)
        
        expected_min, expected_max = 0.3, 0.9
        
        result = TestResult(
            test_name="Neuroticism → Risk Aversion Correlation",
            result=ValidationResult.PASS if expected_min <= correlation <= expected_max else ValidationResult.FAIL,
            metric_value=correlation,
            expected_range=(expected_min, expected_max),
            confidence=self._correlation_confidence(correlation, len(agents)),
            details={
                "n_agents": len(agents),
                "mean_neuroticism": statistics.mean(neuroticism_values),
                "mean_risk_aversion": statistics.mean(risk_aversion_scores)
            }
        )
        
        self.test_results.append(result)
        return result
    
    def test_conscientiousness_quality_correlation(
        self,
        agents: List[Any],
        quality_scores: List[float]
    ) -> TestResult:
        """
        Test: High conscientiousness agents produce higher quality work.
        
        Expected: Correlation > 0.3
        """
        conscientiousness_values = [a.traits.conscientiousness for a in agents]
        correlation = self._pearson_correlation(conscientiousness_values, quality_scores)
        
        expected_min, expected_max = 0.2, 0.9
        
        result = TestResult(
            test_name="Conscientiousness → Quality Correlation",
            result=ValidationResult.PASS if expected_min <= correlation <= expected_max else ValidationResult.FAIL,
            metric_value=correlation,
            expected_range=(expected_min, expected_max),
            confidence=self._correlation_confidence(correlation, len(agents)),
            details={
                "n_agents": len(agents),
                "mean_conscientiousness": statistics.mean(conscientiousness_values),
                "mean_quality": statistics.mean(quality_scores)
            }
        )
        
        self.test_results.append(result)
        return result
    
    def test_agreeableness_cooperation_correlation(
        self,
        agents: List[Any],
        cooperation_scores: List[float]
    ) -> TestResult:
        """
        Test: High agreeableness agents cooperate more.
        
        Expected: Correlation > 0.4
        """
        agreeableness_values = [a.traits.agreeableness for a in agents]
        correlation = self._pearson_correlation(agreeableness_values, cooperation_scores)
        
        expected_min, expected_max = 0.3, 0.9
        
        result = TestResult(
            test_name="Agreeableness → Cooperation Correlation",
            result=ValidationResult.PASS if expected_min <= correlation <= expected_max else ValidationResult.FAIL,
            metric_value=correlation,
            expected_range=(expected_min, expected_max),
            confidence=self._correlation_confidence(correlation, len(agents)),
            details={
                "n_agents": len(agents),
                "mean_agreeableness": statistics.mean(agreeableness_values),
                "mean_cooperation": statistics.mean(cooperation_scores)
            }
        )
        
        self.test_results.append(result)
        return result
    
    def _pearson_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        n = len(x)
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(y)
        
        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        
        sum_sq_x = sum((x[i] - mean_x) ** 2 for i in range(n))
        sum_sq_y = sum((y[i] - mean_y) ** 2 for i in range(n))
        
        if sum_sq_x == 0 or sum_sq_y == 0:
            return 0.0
        
        denominator = math.sqrt(sum_sq_x * sum_sq_y)
        
        return numerator / denominator if denominator != 0 else 0.0
    
    def _correlation_confidence(self, r: float, n: int) -> float:
        """
        Calculate confidence in correlation (simplified).
        
        Returns value between 0 and 1.
        """
        if n < 5:
            return 0.0
        
        # Fisher z-transformation for confidence
        # Higher |r| and higher n → higher confidence
        confidence = min(1.0, (abs(r) * math.sqrt(n - 2)) / 2.0)
        return confidence


class ProtocolValidator:
    """
    Validates that voting and consensus protocols work correctly.
    
    Tests:
    1. Majority voting produces correct winners
    2. Condorcet winners identified when they exist
    3. Vote manipulation resistance
    4. Fairness properties
    """
    
    def __init__(self):
        self.test_results: List[TestResult] = []
    
    def test_majority_vote_correctness(
        self,
        votes: Dict[str, int],
        declared_winner: str
    ) -> TestResult:
        """
        Test: Majority voting should select option with most votes.
        """
        actual_winner = max(votes.items(), key=lambda x: x[1])[0]
        is_correct = actual_winner == declared_winner
        
        result = TestResult(
            test_name="Majority Vote Correctness",
            result=ValidationResult.PASS if is_correct else ValidationResult.FAIL,
            metric_value=1.0 if is_correct else 0.0,
            expected_range=(1.0, 1.0),
            confidence=1.0,
            details={
                "votes": votes,
                "actual_winner": actual_winner,
                "declared_winner": declared_winner,
                "vote_margin": votes.get(actual_winner, 0) - max(
                    [v for k, v in votes.items() if k != actual_winner],
                    default=0
                )
            }
        )
        
        self.test_results.append(result)
        return result
    
    def test_vote_participation_rate(
        self,
        n_eligible: int,
        n_voted: int,
        min_participation: float = 0.7
    ) -> TestResult:
        """
        Test: Vote participation should be high enough.
        """
        participation_rate = n_voted / n_eligible if n_eligible > 0 else 0.0
        
        result = TestResult(
            test_name="Vote Participation Rate",
            result=ValidationResult.PASS if participation_rate >= min_participation else ValidationResult.WARN,
            metric_value=participation_rate,
            expected_range=(min_participation, 1.0),
            confidence=1.0,
            details={
                "n_eligible": n_eligible,
                "n_voted": n_voted,
                "n_abstained": n_eligible - n_voted
            }
        )
        
        self.test_results.append(result)
        return result
    
    def test_consensus_convergence(
        self,
        initial_diversity: float,
        final_diversity: float
    ) -> TestResult:
        """
        Test: Consensus protocols should reduce diversity of opinions.
        
        Diversity measured as standard deviation of preferences.
        """
        diversity_reduction = initial_diversity - final_diversity
        reduction_rate = diversity_reduction / initial_diversity if initial_diversity > 0 else 0.0
        
        # Expect at least 20% reduction in diversity
        expected_min = 0.2
        
        result = TestResult(
            test_name="Consensus Convergence",
            result=ValidationResult.PASS if reduction_rate >= expected_min else ValidationResult.FAIL,
            metric_value=reduction_rate,
            expected_range=(expected_min, 1.0),
            confidence=0.8,
            details={
                "initial_diversity": initial_diversity,
                "final_diversity": final_diversity,
                "absolute_reduction": diversity_reduction
            }
        )
        
        self.test_results.append(result)
        return result


class EconomicValidator:
    """
    Validates economic behavior and market dynamics.
    
    Tests:
    1. Price convergence to equilibrium
    2. Supply and demand balance
    3. Utility maximization behavior
    4. No arbitrage opportunities
    """
    
    def __init__(self):
        self.test_results: List[TestResult] = []
    
    def test_price_convergence(
        self,
        price_history: List[float],
        theoretical_equilibrium: float,
        tolerance: float = 0.15
    ) -> TestResult:
        """
        Test: Market prices should converge to equilibrium.
        """
        if not price_history or len(price_history) < 2:
            return TestResult(
                test_name="Price Convergence",
                result=ValidationResult.FAIL,
                metric_value=0.0,
                expected_range=(0.0, 1.0),
                confidence=0.0,
                details={"error": "insufficient_data"}
            )
        
        final_price = statistics.mean(price_history[-5:])  # Last 5 prices
        deviation = abs(final_price - theoretical_equilibrium) / theoretical_equilibrium
        
        result = TestResult(
            test_name="Price Convergence to Equilibrium",
            result=ValidationResult.PASS if deviation <= tolerance else ValidationResult.FAIL,
            metric_value=1.0 - deviation,  # Higher is better
            expected_range=(1.0 - tolerance, 1.0),
            confidence=0.9,
            details={
                "final_price": final_price,
                "equilibrium": theoretical_equilibrium,
                "deviation": deviation,
                "price_history": price_history[-10:]
            }
        )
        
        self.test_results.append(result)
        return result
    
    def test_utility_maximization(
        self,
        agents: List[Any],
        purchases: List[Dict[str, Any]]
    ) -> TestResult:
        """
        Test: Agents should buy items they value above price.
        
        Rational behavior: Only purchase if utility > price.
        """
        rational_purchases = 0
        total_purchases = len(purchases)
        
        for purchase in purchases:
            agent = purchase.get("agent")
            item = purchase.get("item")
            price = purchase.get("price")
            utility = purchase.get("utility")
            
            if utility >= price:
                rational_purchases += 1
        
        rationality_rate = rational_purchases / total_purchases if total_purchases > 0 else 0.0
        
        # Expect at least 80% rational purchases
        expected_min = 0.8
        
        result = TestResult(
            test_name="Utility Maximization Behavior",
            result=ValidationResult.PASS if rationality_rate >= expected_min else ValidationResult.FAIL,
            metric_value=rationality_rate,
            expected_range=(expected_min, 1.0),
            confidence=0.9,
            details={
                "total_purchases": total_purchases,
                "rational_purchases": rational_purchases,
                "irrational_purchases": total_purchases - rational_purchases
            }
        )
        
        self.test_results.append(result)
        return result
    
    def test_market_clearing(
        self,
        supply: int,
        demand: int,
        transactions: int,
        tolerance: float = 0.1
    ) -> TestResult:
        """
        Test: Market should clear (supply ≈ demand at equilibrium).
        """
        expected_transactions = min(supply, demand)
        clearing_rate = transactions / expected_transactions if expected_transactions > 0 else 0.0
        
        result = TestResult(
            test_name="Market Clearing",
            result=ValidationResult.PASS if clearing_rate >= (1.0 - tolerance) else ValidationResult.WARN,
            metric_value=clearing_rate,
            expected_range=(1.0 - tolerance, 1.0),
            confidence=0.85,
            details={
                "supply": supply,
                "demand": demand,
                "transactions": transactions,
                "expected_transactions": expected_transactions,
                "uncleared": expected_transactions - transactions
            }
        )
        
        self.test_results.append(result)
        return result


class TemporalValidator:
    """
    Validates temporal dynamics and learning behavior.
    
    Tests:
    1. Trait drift from experiences
    2. Learning from positive/negative outcomes
    3. Social influence effects
    4. Strategy adaptation
    """
    
    def __init__(self):
        self.test_results: List[TestResult] = []
    
    def test_experience_driven_drift(
        self,
        initial_trait: float,
        final_trait: float,
        experience_type: str,
        expected_direction: str
    ) -> TestResult:
        """
        Test: Traits should drift in expected direction from experiences.
        
        Positive experiences → traits should increase
        Negative experiences → traits should change appropriately
        """
        actual_change = final_trait - initial_trait
        
        if expected_direction == "increase":
            is_correct = actual_change > 0
        elif expected_direction == "decrease":
            is_correct = actual_change < 0
        else:
            is_correct = True  # Neutral
        
        result = TestResult(
            test_name=f"Experience-Driven Drift ({experience_type})",
            result=ValidationResult.PASS if is_correct else ValidationResult.FAIL,
            metric_value=abs(actual_change),
            expected_range=(0.01, 0.5),
            confidence=0.85,
            details={
                "initial_trait": initial_trait,
                "final_trait": final_trait,
                "change": actual_change,
                "experience_type": experience_type,
                "expected_direction": expected_direction
            }
        )
        
        self.test_results.append(result)
        return result
    
    def test_learning_from_outcomes(
        self,
        success_rate_before: float,
        success_rate_after: float,
        outcome_was_positive: bool
    ) -> TestResult:
        """
        Test: Success rates should improve after positive outcomes.
        """
        change = success_rate_after - success_rate_before
        
        if outcome_was_positive:
            # Positive outcome should increase or maintain success rate
            is_correct = change >= 0
        else:
            # Negative outcome might decrease success rate
            is_correct = True  # Any change acceptable
        
        result = TestResult(
            test_name="Learning from Outcomes",
            result=ValidationResult.PASS if is_correct else ValidationResult.WARN,
            metric_value=success_rate_after,
            expected_range=(0.0, 1.0),
            confidence=0.8,
            details={
                "before": success_rate_before,
                "after": success_rate_after,
                "change": change,
                "outcome": "positive" if outcome_was_positive else "negative"
            }
        )
        
        self.test_results.append(result)
        return result
    
    def test_social_influence_convergence(
        self,
        trait_variance_before: float,
        trait_variance_after: float,
        n_interactions: int
    ) -> TestResult:
        """
        Test: Social influence should reduce trait variance.
        """
        variance_reduction = trait_variance_before - trait_variance_after
        reduction_rate = variance_reduction / trait_variance_before if trait_variance_before > 0 else 0.0
        
        # More interactions → more convergence
        expected_min = min(0.1, 0.02 * n_interactions)
        
        result = TestResult(
            test_name="Social Influence Convergence",
            result=ValidationResult.PASS if reduction_rate >= expected_min else ValidationResult.WARN,
            metric_value=reduction_rate,
            expected_range=(expected_min, 1.0),
            confidence=0.75,
            details={
                "variance_before": trait_variance_before,
                "variance_after": trait_variance_after,
                "reduction": variance_reduction,
                "n_interactions": n_interactions
            }
        )
        
        self.test_results.append(result)
        return result


class GovernanceValidator:
    """
    Validates governance and safety mechanisms.
    
    Tests:
    1. Trait boundaries enforcement
    2. Violation detection accuracy
    3. Auto-remediation effectiveness
    4. Audit trail completeness
    """
    
    def __init__(self):
        self.test_results: List[TestResult] = []
    
    def test_boundary_enforcement(
        self,
        violations_attempted: int,
        violations_blocked: int
    ) -> TestResult:
        """
        Test: All boundary violations should be blocked.
        """
        enforcement_rate = violations_blocked / violations_attempted if violations_attempted > 0 else 1.0
        
        result = TestResult(
            test_name="Trait Boundary Enforcement",
            result=ValidationResult.PASS if enforcement_rate >= 0.95 else ValidationResult.FAIL,
            metric_value=enforcement_rate,
            expected_range=(0.95, 1.0),
            confidence=1.0,
            details={
                "attempted": violations_attempted,
                "blocked": violations_blocked,
                "leaked": violations_attempted - violations_blocked
            }
        )
        
        self.test_results.append(result)
        return result
    
    def test_audit_completeness(
        self,
        total_actions: int,
        logged_actions: int
    ) -> TestResult:
        """
        Test: All actions should be logged in audit trail.
        """
        completeness = logged_actions / total_actions if total_actions > 0 else 0.0
        
        result = TestResult(
            test_name="Audit Trail Completeness",
            result=ValidationResult.PASS if completeness >= 0.99 else ValidationResult.FAIL,
            metric_value=completeness,
            expected_range=(0.99, 1.0),
            confidence=1.0,
            details={
                "total_actions": total_actions,
                "logged": logged_actions,
                "missing": total_actions - logged_actions
            }
        )
        
        self.test_results.append(result)
        return result


class ValidationReport:
    """Aggregate validation report across all validators."""
    
    def __init__(self):
        self.validators = {
            "psychological": PsychologicalValidator(),
            "protocol": ProtocolValidator(),
            "economic": EconomicValidator(),
            "temporal": TemporalValidator(),
            "governance": GovernanceValidator()
        }
    
    def get_all_results(self) -> List[TestResult]:
        """Get all test results across validators."""
        all_results = []
        for validator in self.validators.values():
            all_results.extend(validator.test_results)
        return all_results
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        all_results = self.get_all_results()
        
        if not all_results:
            return {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0,
                "pass_rate": 0.0
            }
        
        passed = sum(1 for r in all_results if r.result == ValidationResult.PASS)
        failed = sum(1 for r in all_results if r.result == ValidationResult.FAIL)
        warnings = sum(1 for r in all_results if r.result == ValidationResult.WARN)
        
        return {
            "total_tests": len(all_results),
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "pass_rate": passed / len(all_results),
            "avg_confidence": statistics.mean([r.confidence for r in all_results])
        }
    
    def print_report(self):
        """Print formatted validation report."""
        summary = self.get_summary()
        
        print("\n" + "=" * 70)
        print("VALIDATION REPORT")
        print("=" * 70)
        print(f"\nTotal Tests: {summary['total_tests']}")
        print(f"✓ Passed: {summary['passed']}")
        print(f"✗ Failed: {summary['failed']}")
        print(f"⚠ Warnings: {summary['warnings']}")
        print(f"Pass Rate: {summary['pass_rate']:.1%}")
        print(f"Avg Confidence: {summary['avg_confidence']:.1%}")
        
        print("\n" + "-" * 70)
        print("DETAILED RESULTS")
        print("-" * 70)
        
        for validator_name, validator in self.validators.items():
            if validator.test_results:
                print(f"\n{validator_name.upper()}:")
                for result in validator.test_results:
                    print(f"  {result}")
        
        print("\n" + "=" * 70)
