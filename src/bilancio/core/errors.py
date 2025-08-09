"""Exception classes for bilancio."""


class BilancioError(Exception):
    """Base exception class for bilancio-related errors."""
    pass


class ValidationError(BilancioError):
    """Raised when data validation fails."""
    pass


class CalculationError(BilancioError):
    """Raised when calculation operations fail."""
    pass


class ConfigurationError(BilancioError):
    """Raised when configuration is invalid or missing."""
    pass


class DefaultError(BilancioError):
    """Raised when a debtor cannot settle their obligations."""
    pass
