"""
Economic capabilities for agents: wallets, utility functions, and preferences.

Extends Citizen agents with economic rationality - ability to value goods,
manage budgets, and make purchasing decisions.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class TransactionType(str, Enum):
    """Types of economic transactions."""
    PURCHASE = "purchase"
    SALE = "sale"
    PAYMENT = "payment"
    REFUND = "refund"
    TRANSFER = "transfer"


class Transaction(BaseModel):
    """A record of an economic transaction."""
    id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    type: TransactionType
    amount: float
    counterparty: str  # Agent name
    item: Optional[str] = None
    description: str = ""
    balance_after: float


class Wallet(BaseModel):
    """
    Economic wallet for an agent.
    
    Tracks balance, transaction history, and spending patterns.
    """
    owner_id: str
    balance: float = 1000.0  # Starting balance
    currency: str = "credits"
    transactions: List[Transaction] = []
    spending_limit: Optional[float] = None  # Max per transaction
    
    def can_afford(self, amount: float) -> bool:
        """Check if wallet has sufficient funds."""
        return self.balance >= amount
    
    def spend(
        self,
        amount: float,
        counterparty: str,
        item: str,
        description: str = ""
    ) -> Transaction:
        """
        Spend money from wallet.
        
        Raises:
            ValueError: If insufficient funds
        """
        if not self.can_afford(amount):
            raise ValueError(
                f"Insufficient funds: need {amount}, have {self.balance}"
            )
        
        if self.spending_limit and amount > self.spending_limit:
            raise ValueError(
                f"Transaction exceeds spending limit: {amount} > {self.spending_limit}"
            )
        
        self.balance -= amount
        
        transaction = Transaction(
            id=f"tx_{len(self.transactions)+1}",
            type=TransactionType.PURCHASE,
            amount=amount,
            counterparty=counterparty,
            item=item,
            description=description,
            balance_after=self.balance
        )
        
        self.transactions.append(transaction)
        return transaction
    
    def receive(
        self,
        amount: float,
        counterparty: str,
        item: str,
        description: str = ""
    ) -> Transaction:
        """Receive money into wallet."""
        self.balance += amount
        
        transaction = Transaction(
            id=f"tx_{len(self.transactions)+1}",
            type=TransactionType.SALE,
            amount=amount,
            counterparty=counterparty,
            item=item,
            description=description,
            balance_after=self.balance
        )
        
        self.transactions.append(transaction)
        return transaction
    
    def get_spending_history(self) -> List[Transaction]:
        """Get all purchase transactions."""
        return [t for t in self.transactions if t.type == TransactionType.PURCHASE]
    
    def total_spent(self) -> float:
        """Calculate total amount spent."""
        return sum(
            t.amount for t in self.transactions 
            if t.type == TransactionType.PURCHASE
        )


class UtilityFunction(BaseModel):
    """
    Utility function defining how an agent values goods.
    
    Maps personality traits and preferences to willingness-to-pay.
    """
    base_value: float  # Base valuation of the item
    risk_adjustment: float = 0.0  # Adjustment based on risk (neuroticism)
    novelty_bonus: float = 0.0  # Bonus for new/innovative (openness)
    social_proof_multiplier: float = 1.0  # Social influence (agreeableness)
    quality_premium: float = 0.0  # Willingness to pay for quality (conscientiousness)
    
    def calculate(
        self,
        agent: Any,
        context: Dict[str, Any] = {}
    ) -> float:
        """
        Calculate agent's utility (willingness-to-pay) for an item.
        
        Args:
            agent: Citizen agent with personality traits
            context: Additional context (reviews, popularity, etc.)
        
        Returns:
            Maximum price agent is willing to pay
        """
        utility = self.base_value
        
        # Openness → values novelty and innovation
        if self.novelty_bonus > 0:
            novelty_factor = agent.traits.openness
            utility += self.novelty_bonus * novelty_factor
        
        # Neuroticism → risk aversion (lowers value)
        if self.risk_adjustment != 0:
            risk_factor = agent.traits.neuroticism
            utility += self.risk_adjustment * risk_factor
        
        # Conscientiousness → quality premium
        if self.quality_premium > 0:
            quality_factor = agent.traits.conscientiousness
            utility += self.quality_premium * quality_factor
        
        # Agreeableness → social proof effect
        if self.social_proof_multiplier != 1.0:
            social_reviews = context.get("reviews", 0)
            social_factor = agent.traits.agreeableness * (social_reviews / 100)
            utility *= (1 + social_factor * (self.social_proof_multiplier - 1))
        
        # Extraversion could influence through network effects
        # (More extraverted = more value in social products)
        network_value = context.get("network_value", 0)
        if network_value > 0:
            extraversion_factor = agent.traits.extraversion
            utility += network_value * extraversion_factor
        
        return max(0, utility)  # Can't be negative


def create_economic_citizen(
    name: str,
    role: str,
    traits: 'PsychologicalProfile',
    initial_balance: float = 1000.0
) -> 'Citizen':
    """
    Create a Citizen with economic capabilities.
    
    This combines personality-driven behavior with economic rationality.
    """
    from simulacrum.agents.persona import Citizen
    
    # Create base citizen
    citizen = Citizen(name=name, role=role, traits=traits)
    
    # Add economic capabilities
    citizen.wallet = Wallet(owner_id=name, balance=initial_balance)
    citizen.purchase_history = []
    
    # Bind helper methods
    citizen.calculate_utility = lambda item, base_value, context={}: calculate_utility(
        citizen, item, base_value, context
    )
    citizen.willing_to_buy = lambda item, price, value=None, context={}: willing_to_buy(
        citizen, item, price, value, context
    )
    citizen.make_purchase = lambda item, price, seller, context={}: make_purchase(
        citizen, item, price, seller, context
    )
    citizen.evaluate_price = lambda item, offered_price, context={}: evaluate_price(
        citizen, item, offered_price, context
    )
    
    return citizen


# Helper function implementations
def calculate_utility(agent, item, base_value, context={}):
    """Calculate utility for an agent."""
    utility_func = UtilityFunction(
        base_value=base_value,
        risk_adjustment=context.get("risk_adjustment", 0),
        novelty_bonus=context.get("novelty_bonus", 0),
        social_proof_multiplier=context.get("social_proof", 1.0),
        quality_premium=context.get("quality_premium", 0)
    )
    return utility_func.calculate(agent, context)


def willing_to_buy(agent, item, price, value=None, context={}):
    """Determine if agent willing to buy."""
    if not agent.wallet.can_afford(price):
        return False
    
    if value is None:
        base_value = context.get("base_value", price * 1.2)
        value = calculate_utility(agent, item, base_value, context)
    
    if value <= price:
        return False
    
    # Personality-based adjustments
    if agent.traits.conscientiousness > 0.7 and value < price * 1.2:
        return False
    if agent.traits.neuroticism > 0.7 and value < price * 1.3:
        return False
    if agent.traits.openness < 0.3 and value < price * 1.5:
        return False
    
    return True


def make_purchase(agent, item, price, seller, context={}):
    """Execute purchase."""
    transaction = agent.wallet.spend(
        amount=price,
        counterparty=seller,
        item=item,
        description=context.get("description", "")
    )
    
    purchase_record = {
        "item": item,
        "price": price,
        "seller": seller,
        "transaction": transaction,
        "timestamp": transaction.timestamp,
        "context": context
    }
    
    agent.purchase_history.append(purchase_record)
    agent.remember(
        f"Purchased {item} from {seller} for {price} credits",
        context="Purchase decision"
    )
    
    return purchase_record


def evaluate_price(agent, item, offered_price, context={}):
    """Evaluate price using agent reasoning."""
    base_value = context.get("base_value", offered_price * 1.2)
    my_value = calculate_utility(agent, item, base_value, context)
    
    prompt = f"""
You are considering purchasing: {item}
Price offered: {offered_price} credits
Your valuation: {my_value:.0f} credits
Your current balance: {agent.wallet.balance:.0f} credits

Context: {context.get('description', 'Standard item')}

Evaluate this price in 2-3 sentences. Is it fair? Would you buy it?
"""
    
    return agent.think(prompt, context="Price evaluation")
