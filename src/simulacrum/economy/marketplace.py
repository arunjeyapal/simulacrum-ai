"""
Marketplace for multi-agent trading and price discovery.

Enables multiple buyers and sellers to interact, with market-clearing
prices emerging from distributed agent decisions.
"""

from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel
from collections import defaultdict
import statistics


class Listing(BaseModel):
    """A seller's listing in the marketplace."""
    seller_id: str
    item: str
    price: float
    quantity: int = 1
    description: str = ""


class MarketTransaction(BaseModel):
    """A completed transaction in the marketplace."""
    buyer_id: str
    seller_id: str
    item: str
    price: float
    quantity: int = 1


class MarketResult(BaseModel):
    """Results from a marketplace simulation."""
    transactions: List[MarketTransaction]
    avg_price: Optional[float] = None
    price_range: Optional[Tuple[float, float]] = None
    total_volume: int = 0
    active_buyers: int = 0
    active_sellers: int = 0
    unsold_listings: List[Listing] = []
    unmatched_buyers: List[str] = []


class Marketplace:
    """
    Simulated marketplace for agent trading.
    
    Features:
    - Multiple buyers and sellers
    - Price discovery through supply/demand
    - Market clearing mechanisms
    - Transaction history
    """
    
    def __init__(self, name: str = "Marketplace"):
        self.name = name
        self.listings: List[Listing] = []
        self.transactions: List[MarketTransaction] = []
    
    def add_listing(
        self,
        seller: Any,
        item: str,
        price: float,
        quantity: int = 1,
        description: str = ""
    ):
        """Seller adds a listing to marketplace."""
        listing = Listing(
            seller_id=seller.name,
            item=item,
            price=price,
            quantity=quantity,
            description=description
        )
        self.listings.append(listing)
        return listing
    
    def get_listings(
        self,
        item: Optional[str] = None,
        max_price: Optional[float] = None
    ) -> List[Listing]:
        """Get available listings, optionally filtered."""
        results = self.listings.copy()
        
        if item:
            results = [l for l in results if l.item == item]
        
        if max_price:
            results = [l for l in results if l.price <= max_price]
        
        # Sort by price (ascending)
        results.sort(key=lambda l: l.price)
        
        return results
    
    def simulate_trading(
        self,
        buyers: List[Any],
        sellers: List[Any],
        item: str,
        context: Dict[str, Any] = {}
    ) -> MarketResult:
        """
        Simulate a trading session with multiple agents.
        
        Process:
        1. Sellers post listings
        2. Buyers evaluate and make purchases
        3. Market clears
        4. Return results
        """
        self.listings = []
        self.transactions = []
        
        # Phase 1: Sellers create listings
        for seller in sellers:
            # Seller decides on asking price
            asking_price = self._seller_price_decision(
                seller, item, context
            )
            
            self.add_listing(
                seller=seller,
                item=item,
                price=asking_price,
                quantity=1,
                description=context.get("description", "")
            )
        
        # Phase 2: Buyers make purchases
        active_buyers = []
        
        for buyer in buyers:
            # Get listings within budget
            affordable = self.get_listings(
                item=item,
                max_price=buyer.wallet.balance
            )
            
            if not affordable:
                continue  # Can't afford anything
            
            # Buyer evaluates listings
            best_listing = self._buyer_purchase_decision(
                buyer, affordable, item, context
            )
            
            if best_listing:
                # Execute transaction
                try:
                    transaction = self._execute_transaction(
                        buyer, best_listing
                    )
                    self.transactions.append(transaction)
                    active_buyers.append(buyer.name)
                    
                    # Remove listing
                    self.listings.remove(best_listing)
                    
                except Exception as e:
                    print(f"Transaction failed: {e}")
                    continue
        
        # Phase 3: Calculate market statistics
        return self._calculate_results(
            buyers, sellers, active_buyers
        )
    
    def _seller_price_decision(
        self,
        seller: Any,
        item: str,
        context: Dict[str, Any]
    ) -> float:
        """Seller decides on listing price."""
        base_value = context.get("base_value", 100)
        
        # Personality-based pricing
        # Openness → higher prices (optimistic)
        # Neuroticism → lower prices (risk averse)
        # Conscientiousness → calculated pricing
        
        if seller.traits.openness > 0.7:
            return base_value * 1.3  # 30% premium
        elif seller.traits.neuroticism > 0.7:
            return base_value * 0.9  # 10% discount
        elif seller.traits.conscientiousness > 0.7:
            return base_value * 1.1  # Careful 10% markup
        else:
            return base_value  # Market rate
    
    def _buyer_purchase_decision(
        self,
        buyer: Any,
        listings: List[Listing],
        item: str,
        context: Dict[str, Any]
    ) -> Optional[Listing]:
        """Buyer decides which listing to purchase."""
        if not listings:
            return None
        
        # Calculate utility for each listing
        best_listing = None
        best_surplus = -float('inf')  # Consumer surplus = value - price
        
        for listing in listings:
            # Calculate value to buyer
            value = buyer.calculate_utility(
                item=item,
                base_value=context.get("base_value", listing.price * 1.2),
                context=context
            )
            
            surplus = value - listing.price
            
            # Buy if positive surplus and best deal
            if surplus > 0 and surplus > best_surplus:
                best_surplus = surplus
                best_listing = listing
        
        return best_listing
    
    def _execute_transaction(
        self,
        buyer: Any,
        listing: Listing
    ) -> MarketTransaction:
        """Execute a purchase transaction."""
        # Buyer pays
        buyer.wallet.spend(
            amount=listing.price,
            counterparty=listing.seller_id,
            item=listing.item,
            description=listing.description
        )
        
        # Record in buyer's history
        buyer.purchase_history.append({
            "item": listing.item,
            "price": listing.price,
            "seller": listing.seller_id,
            "marketplace": self.name
        })
        
        return MarketTransaction(
            buyer_id=buyer.name,
            seller_id=listing.seller_id,
            item=listing.item,
            price=listing.price,
            quantity=listing.quantity
        )
    
    def _calculate_results(
        self,
        buyers: List[Any],
        sellers: List[Any],
        active_buyers: List[str]
    ) -> MarketResult:
        """Calculate market statistics."""
        if not self.transactions:
            return MarketResult(
                transactions=[],
                active_buyers=0,
                active_sellers=0,
                unsold_listings=self.listings,
                unmatched_buyers=[b.name for b in buyers]
            )
        
        prices = [t.price for t in self.transactions]
        
        return MarketResult(
            transactions=self.transactions,
            avg_price=statistics.mean(prices) if prices else None,
            price_range=(min(prices), max(prices)) if prices else None,
            total_volume=len(self.transactions),
            active_buyers=len(set(active_buyers)),
            active_sellers=len(set(t.seller_id for t in self.transactions)),
            unsold_listings=self.listings,
            unmatched_buyers=[
                b.name for b in buyers 
                if b.name not in active_buyers
            ]
        )


def simulate_market(
    buyers: List[Any],
    sellers: List[Any],
    item: str,
    base_value: float = 100,
    context: Dict[str, Any] = {}
) -> MarketResult:
    """
    Convenience function to simulate a market.
    
    Example:
        result = simulate_market(
            buyers=[alice, bob, charlie],
            sellers=[diana, eve],
            item="Premium Feature License",
            base_value=150
        )
        
        print(f"Avg price: ${result.avg_price}")
        print(f"Volume: {result.total_volume} units")
    """
    market = Marketplace()
    
    context.update({
        "base_value": base_value,
        "item": item
    })
    
    return market.simulate_trading(buyers, sellers, item, context)


def analyze_price_sensitivity(
    buyers: List[Any],
    sellers: List[Any],
    item: str,
    price_range: Tuple[float, float],
    steps: int = 10
) -> Dict[float, int]:
    """
    Analyze how many units would sell at different prices.
    
    Returns demand curve: {price: quantity_demanded}
    """
    min_price, max_price = price_range
    step_size = (max_price - min_price) / steps
    
    demand_curve = {}
    
    for i in range(steps + 1):
        price = min_price + (i * step_size)
        
        # Count how many buyers would purchase at this price
        quantity = 0
        
        for buyer in buyers:
            # Simple utility calculation
            value = buyer.calculate_utility(
                item=item,
                base_value=price * 1.5,  # Assume some value premium
                context={}
            )
            
            if value > price and buyer.wallet.can_afford(price):
                quantity += 1
        
        demand_curve[round(price, 2)] = quantity
    
    return demand_curve
