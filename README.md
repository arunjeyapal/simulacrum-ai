# Simulacrum: Synthetic Citizens & Multi-Agent Societies

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Architecting Synthetic Societies, Distributed Protocols, and the Future of Agentic AI**

Simulacrum is an open-source framework for creating AI agents with psychological consistency, memory, and emergent behavior. Move beyond static user personas to dynamic behavioral simulations.

📰 **Featured in LinkedIn Newsletter**: ["The Simulation Layer"](https://www.linkedin.com/newsletters/the-simulation-layer-7425530387369472000)

---

## 🎯 What is Simulacrum?

Traditional user personas give you demographics. Simulacrum gives you **behavioral predictions**.

```python
from simulacrum.agents.persona import Citizen, PsychologicalProfile

# Create a synthetic citizen with specific personality
citizen = Citizen(
    name="Alex",
    role="Tech Enthusiast",
    traits=PsychologicalProfile(
        openness=0.9,           # Loves innovation
        conscientiousness=0.3,  # Impulsive
        neuroticism=0.1         # Calm
    )
)

# Test your product messaging
reaction = citizen.think(
    "Introducing AI-powered email that writes itself!"
)

print(reaction)
# Output: "Finally! I've been waiting for this. Sign me up!"
```

---

## ✨ Key Features

### 🧠 Psychological Realism
- **Big Five Personality Model**: Grounded in 50+ years of psychology research
- **Behavioral Consistency**: Agents react authentically across different scenarios
- **Trait-Based Responses**: High neuroticism = anxiety, high openness = curiosity

### 💾 Memory Systems
- **Episodic Memory**: Agents remember past interactions
- **Contextual Responses**: References previous conversations
- **Temporal Tracking**: Timestamped memory entries

### 🏭 Production-Ready
- **Type-Safe**: Pydantic validation ensures data integrity
- **Model-Agnostic**: Works with OpenAI, Anthropic, Google, or local LLMs
- **Tested**: Comprehensive test suite with 30+ unit tests
- **Extensible**: Factory patterns, composable traits

### 📊 Rich Visualization
- Beautiful terminal output using Rich library
- Comparative analysis tables
- Behavioral consistency reports

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/arunjeyapal/simulacrum-ai.git
cd simulacrum-ai

# Install dependencies
pip install -r requirements.txt

# Set up your API keys
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY or other LLM credentials
```

### Run the Demo

```bash
python examples/01_synthetic_citizens_demo.py
```

This will:
1. Create 3 distinct synthetic citizens (Early Adopter, Skeptic, Anxious User)
2. Test them with product announcements
3. Test them with crisis communication
4. Show behavioral consistency across scenarios

### Create Your First Citizen (60 seconds)

```python
from simulacrum.agents.persona import create_early_adopter

# Use a pre-built archetype
alex = create_early_adopter(name="Alex")

# Test your messaging
reaction = alex.think("We're launching a cryptocurrency product!")
print(reaction)

# Check memory
print(alex.get_memory_summary())
```

---

## 📚 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get running in 5 minutes
- **[Technical Deep Dive](ARTICLE_1_TECHNICAL_GUIDE.md)** - Architecture and research foundations
- **[API Reference](docs/API.md)** - Complete API documentation
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute

---

## 💡 Use Cases

### 1. Product Testing
Test messaging with diverse psychological profiles before launch:

```python
from simulacrum.agents.persona import (
    create_early_adopter,
    create_skeptic,
    create_anxious_user
)

message = "AI that automatically manages your finances while you sleep"

citizens = [
    create_early_adopter(),
    create_skeptic(),
    create_anxious_user()
]

for citizen in citizens:
    print(f"{citizen.name}: {citizen.think(message)}")
```

**Output:**
- Early Adopter: "Finally! Automation is the future!"
- Skeptic: "Show me the security certifications first."
- Anxious User: "Automatically? That makes me nervous..."

### 2. Crisis Communication
Test how different personalities respond to emergency notifications:

```python
crisis = "Service will be down for 48 hours due to technical issues"

for citizen in citizens:
    reaction = citizen.think(crisis)
    action = citizen.think("What will you do next?")
    print(f"{citizen.name}: {reaction} → {action}")
```

### 3. Policy Design
Simulate reactions to organizational changes:

```python
policy = "Starting next month, all employees use biometric login"

# Create 100 employees with diverse traits
employees = [create_diverse_citizen() for _ in range(100)]

reactions = [emp.think(policy) for emp in employees]
sentiment_analysis(reactions)  # Predict adoption vs. resistance
```

### 4. Research
Study behavioral patterns across personality types:

```python
# Test risk tolerance across neuroticism levels
for neuroticism in [0.1, 0.5, 0.9]:
    citizen = Citizen(
        traits=PsychologicalProfile(neuroticism=neuroticism, ...)
    )
    reaction = citizen.think("50% chance of success")
    log_risk_response(neuroticism, reaction)
```

---

## 🗺️ Project Roadmap

### ✅ Phase 1: Synthetic Citizens (Current - Article 1)
- [x] Big Five personality implementation
- [x] Memory systems
- [x] Factory functions for common archetypes
- [x] Comprehensive test suite
- [x] Rich visualization

### ✅ Phase 2: Distributed Protocols (Article 2 - Coming Soon)
- [x] Jury deliberation simulations
- [x] Voting mechanisms (majority, weighted, ranked-choice)
- [x] Consensus protocols
- [x] Multi-agent coordination

### 📋 Phase 3: Agent Economies (Article 3)
- [x] Token-based transactions
- [x] Agent-to-agent negotiations
- [x] Marketplace dynamics
- [x] Resource allocation

### 🔬 Phase 4: Algorithmic Evolution (Article 4)
- [ ] Long-running simulations
- [ ] Behavioral drift detection
- [ ] Communication pattern analysis
- [ ] Diachronic studies

### 🛡️ Phase 5: Governance (Article 5)
- [ ] Safety constraints
- [ ] Bias detection
- [ ] Transparency tools
- [ ] Ethical guidelines

---

## 🏗️ Architecture

```
simulacrum-ai/
├── src/simulacrum/
│   ├── core/              # LLM engine, memory, logging
│   ├── agents/            # Citizen implementation
│   ├── protocols/         # Multi-agent coordination
│   ├── economy/           # Token systems (Phase 3)
│   └── evolution/         # Diachronic AI (Phase 4)
├── examples/              # Runnable demonstrations
├── tests/                 # Test suite
└── docs/                  # Documentation
```

---

## 🔬 Research Foundations

### Psychology
- **Big Five Model**: Costa & McCrae (1992), John & Srivastava (1999)
- **Behavioral Prediction**: Judge et al. (2002)
- **Trait Stability**: Roberts & DelVecchio (2000)

### AI & Simulation
- **Generative Agents**: Park et al. (2023) - Stanford
- **LLMs as Economic Agents**: Horton (2023) - MIT
- **Constitutional AI**: Anthropic (2024)

### Applied Methodology
- Nielsen Norman Group - User research principles
- Kahneman & Tversky - Behavioral economics
- IRB Guidelines - Simulation ethics

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Priority Areas:**
- New personality archetypes
- Calibration studies (synthetic vs. real users)
- Cultural trait systems beyond Big Five
- Emotional dynamics modeling
- Performance optimizations

---

## 📊 Validation & Limitations

### ✅ What This Provides
- Behavioral variance across personality types
- Consistency within individual agents
- Memory-based contextual responses
- Scalable simulations (100s of agents)

### ⚠️ Current Limitations
- No ground truth validation against real cohorts
- Big Five has Western cultural origins
- Static traits (real personalities evolve)
- No emotional dynamics (mood, fatigue)
- Prompt engineering sensitivity

**Recommended Usage:**
- Hypothesis generation (not final decisions)
- Scenario planning and A/B testing
- Complement (not replace) human research
- Always disclose "synthetic" nature to stakeholders

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file

**Dependencies:**
- Pydantic (MIT)
- LiteLLM (MIT)
- Rich (MIT)
- Tenacity (Apache 2.0)

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/arunjeyapal/simulacrum-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/arunjeyapal/simulacrum-ai/discussions)
- **Email**: [contact@arunjayapal.com]
- **LinkedIn**: Connect with the author at [[Your LinkedIn Profile]](https://linkedin.com/in/arunjeyapal)

---

## 🌟 Star History

If you find this project useful, please consider starring it on GitHub!

---

## 📰 Newsletter Series: "The Simulation Layer"

This project accompanies a 5-part LinkedIn newsletter series:

1. **[The Rise of Synthetic Citizens](https://www.linkedin.com/pulse/rise-synthetic-citizens-beyond-static-personas-jayapal-phd-in-cs-bt4lc)** - (Released Feb 17)
2. **[The Elegance of the Swarm](https://www.linkedin.com/pulse/elegance-swarm-distributed-agentic-protocols-arun-jayapal-phd-in-cs-c50gc)** - Distributed protocols - (Released Feb 24)
3. **[The Agent-to-Agent Economy](https://www.linkedin.com/pulse/agent-to-agent-economy-when-ai-learns-transact-jayapal-phd-in-cs-eelvc)**- Autonomous marketplaces ← You are here
4. **Algorithmic Evolution** - Diachronic AI (Coming Mar 10)
5. **Governance as Architecture** - AI safety at scale (Coming Mar 17)

Subscribe to the newsletter: [[LinkedIn Newsletter Link]](https://www.linkedin.com/newsletters/the-simulation-layer-7425530387369472000)

---

## 🙏 Acknowledgments

- Costa & McCrae for Big Five taxonomy
- Park et al. for Generative Agents inspiration
- Anthropic, OpenAI, Google for LLM APIs
- The open-source community

---

## 📈 Project Stats

![GitHub stars](https://img.shields.io/github/stars/arunjeyapal/simulacrum-ai?style=social)
![GitHub forks](https://img.shields.io/github/forks/arunjeyapal/simulacrum-ai?style=social)
![GitHub issues](https://img.shields.io/github/issues/arunjeyapal/simulacrum-ai)
![GitHub pull requests](https://img.shields.io/github/issues-pr/arunjeyapal/simulacrum-ai)

---

**Built with ❤️ by [Arun Jayapal](https://linkedin.com/in/arunjeyapal)**

*"The future isn't about predicting what users will do. It's about simulating who they are."*
