# Simulacrum: Digital Twins & Behavioral AI

**Production-ready framework for creating digital twins and simulating human behavior.**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 🚀 Quick Start

```python
from simulacrum import DigitalTwin

# Create your digital twin from a personality survey
twin = DigitalTwin.from_survey(survey_responses, name="Alice")

# Simulate how you'd make a decision
decision = twin.simulate_decision(
    "Should I accept this job offer?",
    context={"salary": 120000, "role": "Senior Engineer"}
)

print(decision.recommendation)  # "Accept" or "Decline"
print(decision.reasoning)        # Natural language explanation
print(decision.confidence)       # 0.85 (85% confident)
```

**That's it!** No complex setup, no configuration files—just import and use.

---

## 📦 Installation

```bash
# From GitHub (recommended for now)
pip install git+https://github.com/arun-jayapal/simulacrum-ai.git

# For development
git clone https://github.com/arun-jayapal/simulacrum-ai.git
cd simulacrum-ai
pip install -e ".[dev]"
```

---

## 🎯 What is Simulacrum?

Simulacrum is a **library-first** framework for:

1. **Digital Twins**: Create AI replicas of specific individuals
2. **Behavioral Simulation**: Model how people make decisions
3. **Team Dynamics**: Simulate group interactions
4. **Validated AI**: Built on scientifically validated foundations

### Digital Twin vs AI Assistant

| AI Assistant | Digital Twin |
|--------------|--------------|
| Helpful AI | AI version of **you** |
| "How can I help you?" | "This is what I would do" |
| Generic | Personalized |
| Reactive | Predictive |

---

## ✨ Key Features

### 🧠 Psychological Accuracy
Built on the Big Five personality model with 70+ years of research validation.

### 🤝 Team Simulations
Simulate team decisions, predict conflicts, optimize collaboration.

### 💰 Economic Behavior
Model budgets, negotiations, and market dynamics.

### 📈 Temporal Evolution
Agents learn and evolve over time based on experiences.

### 🛡️ Safety First
Governance, audit trails, and explainability built-in.

### 🔬 Scientifically Validated
- 100% internal validation (15/15 tests passed)
- 88.9% research replication (8/9 studies)
- Validates against Nobel Prize research

---

## 📖 Usage Examples

### Create Digital Twin from Survey

```python
from simulacrum import create_twin_from_survey

# User answers 50-question personality survey
twin = create_twin_from_survey(
    survey_responses,
    name="Alice",
    enable_memory=True
)

# Check calibration
print(f"Calibration: {twin.get_calibration_score():.0%}")
```

### Simulate Decisions

```python
# Personal decision
decision = twin.simulate_decision(
    "Accept job offer at startup?",
    context={
        "salary": 100000,
        "equity": "0.5%",
        "risk": "high"
    }
)

print(f"Recommendation: {decision.recommendation}")
print(f"Why: {decision.reasoning}")
```

### Calibrate Accuracy

```python
# Test twin against known decisions
test_scenarios = [
    {"question": "Take risky investment?", "context": {...}},
    {"question": "Confront colleague?", "context": {...}},
    # ... 10-20 scenarios
]
actual_choices = ["Decline", "Accept", ...]

accuracy = twin.calibrate(test_scenarios, actual_choices)
print(f"Twin accuracy: {accuracy:.0%}")
```

### Team Digital Twins

```python
from simulacrum import create_team_twin

# Create team from individual twins
team = create_team_twin([alice_twin, bob_twin, carol_twin])

# Simulate team decision
decision = team.simulate_team_decision(
    "Launch AI feature at $25K cost?",
    voting_method="consensus"
)

print(f"Outcome: {decision.outcome}")
print(f"Consensus: {decision.consensus_strength:.0%}")
```

### Integration Example

```python
# In your application
from simulacrum import DigitalTwin

class CareerAdvisor:
    def __init__(self, user_profile):
        self.twin = DigitalTwin.from_survey(
            user_profile["survey"],
            name=user_profile["name"]
        )
    
    def evaluate_offers(self, job_offers):
        results = []
        for offer in job_offers:
            decision = self.twin.simulate_decision(
                f"Accept {offer['company']} offer?",
                context=offer
            )
            results.append({
                "company": offer["company"],
                "recommendation": decision.recommendation,
                "confidence": decision.confidence
            })
        return results
```

---

## 🏗️ Architecture

Simulacrum is built in **8 layers**:

1. **Individual Psychology** (Big Five traits, memory)
2. **Collective Protocols** (Voting, consensus, deliberation)
3. **Economic Behavior** (Wallets, negotiation, markets)
4. **Temporal Dynamics** (Learning, evolution, adaptation)
5. **Governance** (Safety, audit trails, constraints)
6. **Integration** (All layers working together)
7. **Validation** (Statistical tests, reproducibility)
8. **Digital Twins** (Personalized replicas) ← **NEW**

Each layer builds on previous layers. You can use any layer independently or combine them.

---

## 🎓 Documentation

- **[Getting Started Guide](docs/getting_started.md)** - Installation and first twin
- **[API Reference](docs/api/)** - Complete API documentation
- **[User Guides](docs/guides/)** - Integration patterns and best practices
- **[Examples](examples/)** - Real-world usage examples
- **[Articles](docs/articles/)** - LinkedIn series explaining concepts

---

## 📊 Validation

Simulacrum is **scientifically validated**:

### Internal Validation (100%)
- 140+ unit tests
- 15 statistical validation tests
- All passing

### External Validation (88.9%)
- Replicates 8/9 classic research studies
- Includes Nobel Prize research (Kahneman)
- Includes foundational psychology (Asch, Barrick & Mount)

**See:** [Research Replication Results](docs/validation/research_replication.md)

---

## 🛠️ Development

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=simulacrum --cov-report=html

# Specific module
pytest tests/test_digital_twin/
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
ruff src/ tests/

# Type check
mypy src/
```

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Areas we'd love help with:**
- Additional personality assessments
- More validation tests
- Real-world integration examples
- Documentation improvements
- Bug reports and fixes

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🔗 Links

- **GitHub**: https://github.com/arunjeyapal/simulacrum-ai
- **Documentation**: https://simulacrum-ai.readthedocs.io
- **LinkedIn Series**: [The Simulation Layer](https://linkedin.com/...)
- **Issues**: https://github.com/arunjeyapal/simulacrum-ai/issues

---

## 📚 Citation

If you use Simulacrum in academic work:

```bibtex
@software{simulacrum2025,
  author = {Jayapal, Arun},
  title = {Simulacrum: Digital Twins and Behavioral AI},
  year = {2025},
  url = {https://github.com/arunjeyapal/simulacrum-ai},
  version = {2.0.0}
}
```

---

## 🌟 Series Background

Simulacrum was built through two LinkedIn article series:

**Series 1: Synthetic Agents (8 articles)**
- Built the foundation: psychology, protocols, economy, evolution, governance
- 9,200 lines of production code
- 100% internally validated
- 88.9% research replication rate

**Series 2: Digital Twins (5 articles)** ← **Current**
- Extends foundation to personal digital twins
- Library-first architecture
- Real-world integration focus
- Ethics and governance emphasis

---

## ✨ What's Next?

**Near-term:**
- PyPI distribution
- More personality assessments
- Enhanced calibration methods
- Additional validation tests

**Medium-term:**
- Multi-twin strategies (work you vs personal you)
- Temporal twins (you at different ages)
- Organizational twins
- API service

**Long-term:**
- Continuous learning
- Legacy twins
- Society-level simulations

---

## 💬 Contact

- **Author**: Arun Jayapal
- **Email**: contact@arunjayapal.com
- **LinkedIn**: https://www.linkedin.com/in/arunjeyapal/

---

**Built with ❤️ for the future of personalized AI**

**Not just built. Not just tested. Scientifically validated.** ✅
