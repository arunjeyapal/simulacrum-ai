"""
Economic capabilities for agents: wallets, negotiation, and markets.

Enables agents to engage in economic transactions with personality-driven
valuation and decision-making.
"""

from simulacrum.economy.wallet import (
    Wallet,
    Transaction,
    TransactionType,
    UtilityFunction,
    create_economic_citizen,
    calculate_utility,
    willing_to_buy,
    make_purchase,
    evaluate_price
)

from simulacrum.economy.negotiation import (
    NegotiationProtocol,
    NegotiationOutcome,
    NegotiationResult,
    Offer,
    negotiate_price
)

from simulacrum.economy.marketplace import (
    Marketplace,
    Listing,
    MarketTransaction,
    MarketResult,
    simulate_market,
    analyze_price_sensitivity
)

__all__ = [
    # Wallet & Economic Capabilities
    "Wallet",
    "Transaction",
    "TransactionType",
    "UtilityFunction",
    "create_economic_citizen",
    "calculate_utility",
    "willing_to_buy",
    "make_purchase",
    "evaluate_price",
    
    # Negotiation
    "NegotiationProtocol",
    "NegotiationOutcome",
    "NegotiationResult",
    "Offer",
    "negotiate_price",
    
    # Marketplace
    "Marketplace",
    "Listing",
    "MarketTransaction",
    "MarketResult",
    "simulate_market",
    "analyze_price_sensitivity",
]
