# Article 3 Technical Guide: Agent-to-Agent Economy

**Complete reference for economic agents, wallets, negotiation, and marketplaces**

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Concepts](#core-concepts)
4. [API Reference](#api-reference)
5. [Common Patterns](#common-patterns)
6. [Integration Guide](#integration-guide)
7. [Troubleshooting](#troubleshooting)
8. [Performance](#performance)
9. [Advanced Topics](#advanced-topics)

---

## Overview

The Economic Layer (Article 3) adds economic capabilities to agents:
- **Wallets**: Budget management and transactions
- **Negotiation**: Price discovery and deal-making
- **Marketplaces**: Multi-agent trading environments
- **Utility Functions**: Value assessment based on personality

**Key Innovation**: Markets emerge from personality-driven individual decisions, not rational actor assumptions.

---

## Architecture

### Layer Stack
```
┌─────────────────────────────────────┐
│      Marketplace                     │  ← Market-level dynamics
│  (Supply/demand, equilibrium)        │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      Negotiation                     │  ← Agent-to-agent
│  (Offers, counteroffers, deals)      │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      Wallet                          │  ← Individual economics
│  (Balance, transactions, budgets)    │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      Persona (Article 1)             │  ← Personality traits
└─────────────────────────────────────┘
```

### File Structure
```
src/simulacrum/economy/
├── __init__.py          # Package exports
├── wallet.py            # Wallet & transactions
├── negotiation.py       # Price negotiation
└── marketplace.py       # Market simulation
```

---

## Core Concepts

### 1. Economic Citizen

An agent with economic capabilities:

```python
from simulacrum.economy import create_economic_citizen

agent = create_economic_citizen(
    name="Alice",
    role="Consumer",
    traits=my_traits,
    initial_balance=1000.0
)

# Agent now has:
# - agent.wallet (balance, transactions)
# - agent.calculate_utility(item, price, context)
# - agent.willing_to_buy(item, price, utility)
# - agent.make_offer(item, max_price)
```

**Key Insight**: Utility calculation is personality-driven:
- High openness → Values novelty
- High neuroticism → Risk-averse pricing
- High conscientiousness → Thorough evaluation

### 2. Wallet System

**Balance Management:**
```python
wallet = Wallet(initial_balance=1000.0)

# Check balance
print(wallet.balance)  # 1000.0

# Check affordability
can_buy = wallet.can_afford(250.0)  # True

# Make transaction
success = wallet.deduct(250.0, "Purchase: Item X")
print(wallet.balance)  # 750.0

# Add funds
wallet.add(500.0, "Income: Salary")
print(wallet.balance)  # 1250.0
```

**Transaction History:**
```python
# View all transactions
for tx in wallet.transactions:
    print(f"{tx.timestamp}: {tx.amount} - {tx.description}")

# Get summary
total_spent = sum(tx.amount for tx in wallet.transactions if tx.amount < 0)
total_earned = sum(tx.amount for tx in wallet.transactions if tx.amount > 0)
```

### 3. Utility Functions

**How agents value items:**

```python
# Agent calculates utility
utility = agent.calculate_utility(
    item_name="Premium Feature",
    price=99.0,
    context={
        "is_novel": True,      # Appeals to openness
        "is_proven": False,    # Concerns neuroticism
        "quality_score": 0.8   # Appeals to conscientiousness
    }
)

# Personality influences utility:
# High openness + novel → Higher utility
# High neuroticism + unproven → Lower utility
# High conscientiousness + quality → Higher utility
```

**Utility Formula:**
```python
base_utility = reference_price * agent_specific_multiplier

# Adjustments based on traits:
if context.get("is_novel") and agent.traits.openness > 0.7:
    utility *= 1.3  # Innovation premium

if context.get("is_risky") and agent.traits.neuroticism > 0.6:
    utility *= 0.7  # Risk discount

# Final decision:
willing_to_buy = utility > price
```

### 4. Negotiation Protocol

**Two-agent price discovery:**

```python
from simulacrum.economy import negotiate_price

result = negotiate_price(
    buyer=buyer_agent,
    seller=seller_agent,
    item_name="Widget",
    initial_price=100.0,
    max_rounds=5
)

if result.deal_reached:
    print(f"Deal at ${result.final_price}")
    print(f"Rounds: {result.rounds_taken}")
else:
    print("No deal")
```

**Negotiation Dynamics:**
- Buyer makes lower offers (based on utility)
- Seller counters higher (based on cost)
- Agreeableness affects compromise speed
- Conscientiousness affects walkaway point

**Example Flow:**
```
Round 1:
  Buyer offers: $80 (knows utility = $110)
  Seller counters: $95 (cost = $70)

Round 2:
  Buyer: $85
  Seller: $92

Round 3:
  Buyer: $88
  Seller: $90

Deal! Final price: $89
```

### 5. Marketplace

**Multi-agent trading:**

```python
from simulacrum.economy import Marketplace

market = Marketplace(name="Widget Market")

# Add participants
for buyer in buyers:
    market.add_buyer(buyer)

for seller in sellers:
    market.add_seller(seller)

# Run trading period
transactions = market.execute_trading_period(
    item_name="Widget",
    supply_quantity=50,
    demand_quantity=45
)

# Analyze results
avg_price = sum(t.price for t in transactions) / len(transactions)
clearing_rate = len(transactions) / min(supply_quantity, demand_quantity)
```

**Market Dynamics:**
- Prices converge to equilibrium over multiple periods
- High demand → prices rise
- High supply → prices fall
- Personality creates variance around equilibrium

---

## API Reference

### Wallet Class

```python
class Wallet:
    def __init__(self, initial_balance: float = 0.0)
    
    @property
    def balance(self) -> float
        """Current balance"""
    
    def can_afford(self, amount: float) -> bool
        """Check if balance >= amount"""
    
    def deduct(
        self,
        amount: float,
        description: str = ""
    ) -> bool
        """
        Deduct from balance.
        Returns True if successful, False if insufficient funds.
        """
    
    def add(
        self,
        amount: float,
        description: str = ""
    ) -> None
        """Add to balance"""
    
    @property
    def transactions(self) -> List[Transaction]
        """All transactions history"""
```

### Economic Citizen Factory

```python
def create_economic_citizen(
    name: str,
    role: str,
    traits: PsychologicalProfile,
    initial_balance: float = 1000.0
) -> Citizen:
    """
    Create agent with economic capabilities.
    
    Adds methods:
    - calculate_utility(item_name, price, context)
    - willing_to_buy(item_name, price, utility)
    - make_offer(item_name, max_price)
    """
```

### Negotiation Function

```python
def negotiate_price(
    buyer: Citizen,
    seller: Citizen,
    item_name: str,
    initial_price: float,
    max_rounds: int = 10
) -> NegotiationResult:
    """
    Two-agent price negotiation.
    
    Returns:
        NegotiationResult with:
        - deal_reached: bool
        - final_price: float
        - rounds_taken: int
        - buyer_surplus: float
        - seller_surplus: float
    """
```

### Marketplace Class

```python
class Marketplace:
    def __init__(self, name: str)
    
    def add_buyer(self, agent: Citizen) -> None
    def add_seller(self, agent: Citizen) -> None
    
    def execute_trading_period(
        self,
        item_name: str,
        supply_quantity: int,
        demand_quantity: int
    ) -> List[Transaction]:
        """
        Run one trading period.
        Returns list of completed transactions.
        """
    
    def get_price_history(self) -> List[float]:
        """Historical prices across periods"""
    
    def get_market_statistics(self) -> Dict[str, Any]:
        """
        Returns:
        - avg_price
        - price_volatility
        - transaction_count
        - clearing_rate
        """
```

---

## Common Patterns

### Pattern 1: Simple Purchase Decision

```python
from simulacrum.economy import create_economic_citizen

# Create buyer
buyer = create_economic_citizen(
    "Alice",
    "Consumer",
    my_traits,
    initial_balance=500.0
)

# Item details
item = "Premium Subscription"
price = 49.99

# Calculate value
utility = buyer.calculate_utility(
    item,
    price,
    context={"is_novel": True}
)

# Make decision
if buyer.willing_to_buy(item, price, utility):
    if buyer.wallet.can_afford(price):
        buyer.wallet.deduct(price, f"Purchase: {item}")
        print(f"Purchased {item} for ${price}")
    else:
        print("Can't afford")
else:
    print(f"Not worth ${price} (utility: ${utility:.2f})")
```

### Pattern 2: Personality-Driven Pricing

```python
# Create diverse buyers
buyers = [
    create_economic_citizen("Innovator", "Early Adopter", 
                          high_openness_traits, 1000),
    create_economic_citizen("Skeptic", "Conservative",
                          low_openness_traits, 1000),
]

# Test price sensitivity
for price in [25, 50, 75, 100]:
    willing = sum(
        1 for b in buyers
        if b.willing_to_buy("New Feature", price,
                           b.calculate_utility("New Feature", price, {}))
    )
    print(f"${price}: {willing}/{len(buyers)} would buy")

# Output:
# $25: 2/2 would buy
# $50: 2/2 would buy
# $75: 1/2 would buy  (skeptic drops out)
# $100: 1/2 would buy (only innovator)
```

### Pattern 3: Two-Agent Negotiation

```python
from simulacrum.economy import negotiate_price

# Create buyer and seller
buyer = create_economic_citizen("Alice", "Buyer", buyer_traits, 1000)
seller = create_economic_citizen("Bob", "Seller", seller_traits, 500)

# Negotiate
result = negotiate_price(
    buyer=buyer,
    seller=seller,
    item_name="Widget",
    initial_price=100.0,
    max_rounds=5
)

if result.deal_reached:
    # Execute transaction
    buyer.wallet.deduct(result.final_price, "Purchase: Widget")
    seller.wallet.add(result.final_price, "Sale: Widget")
    
    print(f"Deal at ${result.final_price}")
    print(f"Buyer surplus: ${result.buyer_surplus:.2f}")
    print(f"Seller surplus: ${result.seller_surplus:.2f}")
```

### Pattern 4: Market Simulation

```python
from simulacrum.economy import Marketplace

# Create market
market = Marketplace("Widget Market")

# Create participants
buyers = [create_economic_citizen(f"Buyer_{i}", "Consumer", 
                                  random_traits(), 1000) 
          for i in range(20)]
sellers = [create_economic_citizen(f"Seller_{i}", "Producer",
                                   random_traits(), 500)
           for i in range(20)]

# Add to market
for b in buyers:
    market.add_buyer(b)
for s in sellers:
    market.add_seller(s)

# Simulate 10 trading periods
price_history = []
for period in range(10):
    transactions = market.execute_trading_period(
        item_name="Widget",
        supply_quantity=20,
        demand_quantity=18
    )
    
    avg_price = sum(t.price for t in transactions) / len(transactions)
    price_history.append(avg_price)
    
    print(f"Period {period}: ${avg_price:.2f}, {len(transactions)} trades")

# Check convergence
print(f"Price range: ${min(price_history):.2f} - ${max(price_history):.2f}")
```

### Pattern 5: Budget-Constrained Decision

```python
# Agent with limited budget
agent = create_economic_citizen("Charlie", "Student", traits, 100.0)

# Multiple purchase options
items = [
    ("Basic Plan", 19.99),
    ("Pro Plan", 49.99),
    ("Premium Plan", 99.99)
]

# Find best affordable option
affordable = []
for item_name, price in items:
    if agent.wallet.can_afford(price):
        utility = agent.calculate_utility(item_name, price, {})
        value_ratio = utility / price  # Utility per dollar
        affordable.append((item_name, price, utility, value_ratio))

if affordable:
    # Choose highest value ratio
    best = max(affordable, key=lambda x: x[3])
    print(f"Best choice: {best[0]} (value ratio: {best[3]:.2f})")
else:
    print("Can't afford any option")
```

---

## Integration Guide

### Integrating with Article 1 (Personas)

```python
from simulacrum.agents import create_early_adopter
from simulacrum.economy import create_economic_citizen

# Start with persona
base_agent = create_early_adopter("Alice")

# Add economic capabilities
economic_agent = create_economic_citizen(
    name=base_agent.name,
    role="Product Manager",
    traits=base_agent.traits,
    initial_balance=5000.0
)

# Now has both:
# - Personality (openness=0.9, etc.)
# - Wallet (balance=$5000)
# - Utility calculation (personality-driven)
```

### Integrating with Article 2 (Protocols)

```python
from simulacrum.protocols import quick_vote
from simulacrum.economy import create_economic_citizen

# Economic team
team = [
    create_economic_citizen(f"Member_{i}", "Team", traits, 1000)
    for i in range(10)
]

# Vote on budget allocation
result = quick_vote(
    team,
    "Approve $50K marketing budget?",
    ["Yes", "No"]
)

# If approved, deduct from team wallets
if result.winner == "Yes":
    cost_per_member = 50000 / len(team)
    for member in team:
        member.wallet.deduct(cost_per_member, "Marketing budget")
```

### Integrating with Article 4 (Evolution)

```python
from simulacrum.evolution import create_temporal_agent
from simulacrum.economy import create_economic_citizen

# Create economic agent
base = create_economic_citizen("Alice", "Trader", traits, 10000)

# Add temporal dynamics
temporal = create_temporal_agent(base, drift_rate=0.02)

# Trade and learn
for day in range(30):
    # Make purchase decision
    utility = temporal.agent.calculate_utility("Stock", 100, {})
    
    if temporal.agent.willing_to_buy("Stock", 100, utility):
        temporal.agent.wallet.deduct(100, "Stock purchase")
        
        # Experience affects traits
        profit = random.randint(-20, 40)
        if profit > 0:
            temporal.add_experience(
                "Profitable trade",
                ExperienceType.POSITIVE,
                trait_impacts={"openness": 0.01}  # Success → more risk-seeking
            )
        else:
            temporal.add_experience(
                "Loss",
                ExperienceType.NEGATIVE,
                trait_impacts={"neuroticism": 0.01}  # Loss → more anxious
            )
```

---

## Troubleshooting

### Problem: Unrealistic Pricing

**Symptom**: All agents willing to pay any price

**Cause**: Utility calculation not considering traits

**Solution**:
```python
# BAD - Ignores personality
def calculate_utility(self, item, price, context):
    return price * 1.5  # Everyone values 50% above price

# GOOD - Personality-driven
def calculate_utility(self, item, price, context):
    base = price * 1.2
    
    # Openness affects novelty premium
    if context.get("is_novel"):
        base *= (1 + self.traits.openness * 0.5)
    
    # Neuroticism affects risk discount
    if context.get("is_risky"):
        base *= (1 - self.traits.neuroticism * 0.4)
    
    return base
```

### Problem: Negotiations Never Converge

**Symptom**: All negotiations hit max_rounds without deal

**Cause**: Buyer and seller ranges don't overlap

**Solution**:
```python
# Check if deal is possible
buyer_max = buyer.calculate_utility(item, 1000, {})  # Max willing to pay
seller_min = 50  # Minimum seller will accept

if buyer_max < seller_min:
    print("No deal possible: ranges don't overlap")
else:
    result = negotiate_price(buyer, seller, item, seller_min, max_rounds=10)
```

### Problem: Market Doesn't Clear

**Symptom**: Few transactions despite ample supply/demand

**Cause**: Prices too far from equilibrium

**Solution**:
```python
# Add price discovery mechanism
current_price = 100.0

for period in range(20):
    transactions = market.execute_trading_period(
        item_name="Widget",
        supply_quantity=50,
        demand_quantity=45
    )
    
    # Adjust price based on clearing
    clearing_rate = len(transactions) / min(50, 45)
    
    if clearing_rate < 0.8:
        # Not clearing → adjust price
        if len(buyers_willing) > len(sellers_willing):
            current_price *= 1.05  # Demand > supply → raise price
        else:
            current_price *= 0.95  # Supply > demand → lower price
```

### Problem: Insufficient Funds Errors

**Symptom**: Agents run out of money quickly

**Cause**: No budget management

**Solution**:
```python
# Add budget checking before purchases
def smart_purchase(agent, item, price):
    # Check affordability
    if not agent.wallet.can_afford(price):
        return False
    
    # Check budget constraint (max 20% of balance)
    if price > agent.wallet.balance * 0.2:
        return False
    
    # Check utility
    utility = agent.calculate_utility(item, price, {})
    if utility <= price:
        return False
    
    # All checks passed
    agent.wallet.deduct(price, f"Purchase: {item}")
    return True
```

---

## Performance

### Benchmarks

**Single Transaction:**
- Calculate utility: <1ms
- Wallet deduct/add: <1ms
- Willing to buy check: <1ms

**Negotiation:**
- 2 agents, 5 rounds: ~15 seconds (includes LLM calls)
- Without LLM (pure math): <10ms

**Market Simulation:**
- 20 buyers, 20 sellers, 1 period: ~2 minutes
- 100 agents, 10 periods: ~25 minutes

**Bottlenecks:**
- LLM API calls for reasoning (can be cached)
- Not the mathematical calculations

### Optimization Strategies

**1. Batch LLM Calls**
```python
# Instead of calling LLM for each agent's reasoning
# Batch multiple agents in one call
responses = await batch_llm_call([
    agent1.reasoning_prompt,
    agent2.reasoning_prompt,
    # ... up to 10
])
```

**2. Cache Utility Calculations**
```python
# Same item, same price, same context → same utility (for same agent)
@lru_cache(maxsize=1000)
def calculate_utility_cached(self, item, price, context_hash):
    return self.calculate_utility(item, price, context)
```

**3. Parallel Market Simulation**
```python
# Run multiple periods in parallel
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [
        executor.submit(market.execute_trading_period, "Widget", 50, 45)
        for _ in range(10)
    ]
    results = [f.result() for f in futures]
```

---

## Advanced Topics

### Custom Utility Functions

```python
# Define domain-specific utility
class CustomEconomicCitizen(Citizen):
    def calculate_utility(self, item, price, context):
        # Start with base
        base = price * 1.1
        
        # Custom logic for your domain
        if item.startswith("B2B"):
            # Business buyers care about ROI
            roi = context.get("roi", 0)
            base *= (1 + roi)
        
        if item.startswith("Consumer"):
            # Consumers care about brand
            brand_score = context.get("brand", 0.5)
            base *= (0.5 + brand_score)
        
        # Apply personality
        if self.traits.openness > 0.7:
            base *= 1.2
        
        return base
```

### Dynamic Pricing Strategies

```python
class DynamicPricer:
    """Seller that adjusts prices based on demand"""
    
    def __init__(self, base_price: float):
        self.base_price = base_price
        self.price_history = []
        self.sales_history = []
    
    def get_current_price(self) -> float:
        if not self.sales_history:
            return self.base_price
        
        # If selling well, raise price
        recent_sales = sum(self.sales_history[-5:])
        if recent_sales >= 4:
            return self.base_price * 1.1
        elif recent_sales <= 1:
            return self.base_price * 0.9
        else:
            return self.base_price
    
    def record_sale(self, sold: bool):
        self.sales_history.append(1 if sold else 0)
```

### Multi-Item Portfolio Optimization

```python
def optimize_portfolio(agent, items, budget):
    """Choose best combination of items within budget"""
    
    # Calculate utility per dollar for each item
    value_ratios = []
    for item_name, price in items:
        utility = agent.calculate_utility(item_name, price, {})
        value_ratios.append((item_name, price, utility/price))
    
    # Sort by value ratio
    value_ratios.sort(key=lambda x: x[2], reverse=True)
    
    # Greedy selection
    selected = []
    remaining_budget = budget
    
    for item_name, price, ratio in value_ratios:
        if price <= remaining_budget:
            selected.append((item_name, price))
            remaining_budget -= price
    
    return selected
```

---

## Best Practices

✅ **DO:**
- Always check `can_afford()` before transactions
- Use personality traits to drive utility calculations
- Log all transactions for audit
- Handle insufficient funds gracefully
- Test with diverse personality profiles

❌ **DON'T:**
- Assume rational actors (agents aren't perfectly rational)
- Ignore budget constraints
- Use fixed utility functions (make them personality-driven)
- Skip validation of transaction success
- Forget to update balances after trades

---

## Further Reading

- **Article 1**: The Rise of Synthetic Citizens - Technical Deep Dive
- **Article 2**: The Elegance of the Swarm
- **Article 3**: The Agent-to-Agent Economy

---

**Next**: Article 4 Technical Guide (Temporal Dynamics & Learning)
