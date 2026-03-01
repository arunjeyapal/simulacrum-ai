"""
Negotiation protocol for buyer-seller interactions.

Enables agents to negotiate prices through multi-round bidding,
with personality-driven negotiation strategies.
"""

from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel
from enum import Enum
from simulacrum.protocols.base import Protocol


class NegotiationOutcome(str, Enum):
    """Possible outcomes of a negotiation."""
    SUCCESS = "success"  # Deal reached
    FAILURE = "failure"  # No agreement
    TIMEOUT = "timeout"  # Max rounds exceeded


class Offer(BaseModel):
    """An offer made during negotiation."""
    round: int
    agent_id: str
    role: str  # "buyer" or "seller"
    price: float
    message: str = ""


class NegotiationResult(BaseModel):
    """Result of a negotiation session."""
    outcome: NegotiationOutcome
    final_price: Optional[float] = None
    rounds_taken: int
    offers: List[Offer]
    buyer_id: str
    seller_id: str
    item: str
    initial_ask: float
    initial_bid: float
    savings: Optional[float] = None  # For buyer (ask - final)
    premium: Optional[float] = None  # For seller (final - bid)


class NegotiationProtocol(Protocol):
    """
    Negotiation protocol for price discovery.
    
    Process:
    1. Seller sets asking price
    2. Buyer makes initial bid
    3. Rounds of counter-offers
    4. Agreement or failure
    
    Personality effects:
    - High agreeableness → quicker agreement, smaller moves
    - High neuroticism → more cautious, slower concessions
    - High openness → creative solutions, larger moves
    - High conscientiousness → careful evaluation, fact-based
    """
    
    def __init__(
        self,
        max_rounds: int = 5,
        min_price_movement: float = 1.0,  # Minimum price change per round
        convergence_threshold: float = 5.0  # Bid-ask within this = deal
    ):
        super().__init__(
            name="Negotiation Protocol",
            description="Buyer-seller price negotiation"
        )
        self.max_rounds = max_rounds
        self.min_price_movement = min_price_movement
        self.convergence_threshold = convergence_threshold
    
    def validate_participation(self, agents: List[Any]) -> bool:
        """Requires exactly 2 agents (buyer and seller)."""
        return len(agents) == 2
    
    def execute(
        self,
        agents: List[Any],
        context: Dict[str, Any]
    ) -> NegotiationResult:
        """
        Execute negotiation between buyer and seller.
        
        Context should contain:
        - item: What's being sold
        - seller_index: Which agent is selling (0 or 1)
        - seller_reserve: Minimum price seller will accept
        - buyer_max: Maximum price buyer will pay
        """
        if not self.validate_participation(agents):
            raise ValueError("Negotiation requires exactly 2 agents")
        
        item = context.get("item", "Product")
        seller_index = context.get("seller_index", 0)
        buyer_index = 1 - seller_index
        
        seller = agents[seller_index]
        buyer = agents[buyer_index]
        
        # Get initial positions
        seller_reserve = context.get("seller_reserve", 100)
        buyer_max = context.get("buyer_max", 200)
        
        # Check if deal is possible
        if seller_reserve > buyer_max:
            return NegotiationResult(
                outcome=NegotiationOutcome.FAILURE,
                rounds_taken=0,
                offers=[],
                buyer_id=buyer.name,
                seller_id=seller.name,
                item=item,
                initial_ask=seller_reserve,
                initial_bid=buyer_max
            )
        
        # Round 0: Initial positions
        initial_ask = self._get_initial_ask(seller, seller_reserve, item, context)
        initial_bid = self._get_initial_bid(buyer, buyer_max, item, context)
        
        offers = [
            Offer(round=0, agent_id=seller.name, role="seller", price=initial_ask, message="Initial ask"),
            Offer(round=0, agent_id=buyer.name, role="buyer", price=initial_bid, message="Initial bid")
        ]
        
        # Check immediate convergence
        if abs(initial_ask - initial_bid) <= self.convergence_threshold:
            final_price = (initial_ask + initial_bid) / 2
            return self._create_success_result(
                buyer, seller, item, final_price, 
                initial_ask, initial_bid, offers
            )
        
        # Multi-round negotiation
        current_ask = initial_ask
        current_bid = initial_bid
        
        for round_num in range(1, self.max_rounds + 1):
            # Seller's turn to counter
            current_ask = self._seller_counter(
                seller, buyer, item, current_ask, current_bid,
                seller_reserve, round_num, context
            )
            
            offers.append(
                Offer(
                    round=round_num,
                    agent_id=seller.name,
                    role="seller",
                    price=current_ask,
                    message=f"Counter-offer"
                )
            )
            
            # Check convergence
            if abs(current_ask - current_bid) <= self.convergence_threshold:
                final_price = (current_ask + current_bid) / 2
                return self._create_success_result(
                    buyer, seller, item, final_price,
                    initial_ask, initial_bid, offers
                )
            
            # Buyer's turn to counter
            current_bid = self._buyer_counter(
                buyer, seller, item, current_bid, current_ask,
                buyer_max, round_num, context
            )
            
            offers.append(
                Offer(
                    round=round_num,
                    agent_id=buyer.name,
                    role="buyer",
                    price=current_bid,
                    message=f"Counter-offer"
                )
            )
            
            # Check convergence again
            if abs(current_ask - current_bid) <= self.convergence_threshold:
                final_price = (current_ask + current_bid) / 2
                return self._create_success_result(
                    buyer, seller, item, final_price,
                    initial_ask, initial_bid, offers
                )
        
        # Timeout: no agreement after max rounds
        return NegotiationResult(
            outcome=NegotiationOutcome.TIMEOUT,
            rounds_taken=self.max_rounds,
            offers=offers,
            buyer_id=buyer.name,
            seller_id=seller.name,
            item=item,
            initial_ask=initial_ask,
            initial_bid=initial_bid
        )
    
    def _get_initial_ask(
        self,
        seller: Any,
        reserve_price: float,
        item: str,
        context: Dict[str, Any]
    ) -> float:
        """Seller sets initial asking price."""
        # Base on reserve with markup
        # Openness → higher markup (willing to try high prices)
        # Neuroticism → lower markup (fear of no sale)
        
        markup_factor = 1.5  # Default 50% markup
        
        if seller.traits.openness > 0.7:
            markup_factor = 1.8  # Ambitious pricing
        elif seller.traits.neuroticism > 0.7:
            markup_factor = 1.2  # Conservative pricing
        
        return reserve_price * markup_factor
    
    def _get_initial_bid(
        self,
        buyer: Any,
        max_price: float,
        item: str,
        context: Dict[str, Any]
    ) -> float:
        """Buyer makes initial bid."""
        # Start low to leave negotiation room
        # Agreeableness → higher initial bid (fair)
        # Conscientiousness → careful, mid-range bid
        
        bid_factor = 0.6  # Default 60% of max
        
        if buyer.traits.agreeableness > 0.7:
            bid_factor = 0.75  # More generous opening
        elif buyer.traits.conscientiousness > 0.7:
            bid_factor = 0.65  # Careful but fair
        
        return max_price * bid_factor
    
    def _seller_counter(
        self,
        seller: Any,
        buyer: Any,
        item: str,
        current_ask: float,
        buyer_bid: float,
        reserve: float,
        round_num: int,
        context: Dict[str, Any]
    ) -> float:
        """Seller makes counter-offer."""
        gap = current_ask - buyer_bid
        
        # Concession size based on personality
        # High agreeableness → larger concessions
        # High conscientiousness → steady, calculated moves
        # High neuroticism → smaller concessions (fear of loss)
        
        if seller.traits.agreeableness > 0.6:
            concession_rate = 0.4  # Move 40% toward buyer
        elif seller.traits.conscientiousness > 0.6:
            concession_rate = 0.3  # Steady 30% moves
        else:
            concession_rate = 0.2  # Cautious 20% moves
        
        # Adjust for pressure (later rounds = more concession)
        pressure_factor = round_num / self.max_rounds
        concession_rate *= (1 + pressure_factor)
        
        new_ask = current_ask - (gap * concession_rate)
        
        # Don't go below reserve
        new_ask = max(new_ask, reserve)
        
        # Ensure minimum movement
        if abs(new_ask - current_ask) < self.min_price_movement:
            new_ask = current_ask - self.min_price_movement
            new_ask = max(new_ask, reserve)
        
        return new_ask
    
    def _buyer_counter(
        self,
        buyer: Any,
        seller: Any,
        item: str,
        current_bid: float,
        seller_ask: float,
        max_price: float,
        round_num: int,
        context: Dict[str, Any]
    ) -> float:
        """Buyer makes counter-offer."""
        gap = seller_ask - current_bid
        
        # Concession size based on personality
        if buyer.traits.agreeableness > 0.6:
            concession_rate = 0.4  # Generous moves
        elif buyer.traits.openness > 0.6:
            concession_rate = 0.35  # Creative, flexible
        else:
            concession_rate = 0.25  # Conservative moves
        
        # Later rounds = more pressure to close
        pressure_factor = round_num / self.max_rounds
        concession_rate *= (1 + pressure_factor)
        
        new_bid = current_bid + (gap * concession_rate)
        
        # Don't exceed max
        new_bid = min(new_bid, max_price)
        
        # Ensure minimum movement
        if abs(new_bid - current_bid) < self.min_price_movement:
            new_bid = current_bid + self.min_price_movement
            new_bid = min(new_bid, max_price)
        
        return new_bid
    
    def _create_success_result(
        self,
        buyer: Any,
        seller: Any,
        item: str,
        final_price: float,
        initial_ask: float,
        initial_bid: float,
        offers: List[Offer]
    ) -> NegotiationResult:
        """Create successful negotiation result."""
        return NegotiationResult(
            outcome=NegotiationOutcome.SUCCESS,
            final_price=final_price,
            rounds_taken=len([o for o in offers if o.round > 0]) // 2,
            offers=offers,
            buyer_id=buyer.name,
            seller_id=seller.name,
            item=item,
            initial_ask=initial_ask,
            initial_bid=initial_bid,
            savings=initial_ask - final_price,
            premium=final_price - initial_bid
        )


def negotiate_price(
    buyer: Any,
    seller: Any,
    item: str,
    seller_reserve: float,
    buyer_max: float,
    max_rounds: int = 5
) -> NegotiationResult:
    """
    Convenience function for price negotiation.
    
    Example:
        result = negotiate_price(
            buyer=alice,
            seller=bob,
            item="Vintage Guitar",
            seller_reserve=500,
            buyer_max=800,
            max_rounds=5
        )
        
        if result.outcome == NegotiationOutcome.SUCCESS:
            print(f"Deal! Price: ${result.final_price}")
    """
    protocol = NegotiationProtocol(max_rounds=max_rounds)
    
    return protocol.execute(
        agents=[seller, buyer],  # Seller first
        context={
            "item": item,
            "seller_index": 0,
            "seller_reserve": seller_reserve,
            "buyer_max": buyer_max
        }
    )
