class TriangularArbitrageError(Exception):
    """Base exception for triangular arbitrage errors."""

class InvalidTradingPairError(TriangularArbitrageError):
    """Raised when trading pairs are invalid for triangular arbitrage."""

class InsufficientBalanceError(TriangularArbitrageError):
    """Raised when there's insufficient balance to execute a trade."""

class OrderPlacementError(TriangularArbitrageError):
    """Raised when an order fails to be placed."""