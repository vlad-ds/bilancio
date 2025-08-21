"""UI settings and configuration for bilancio display."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Central configuration for UI display settings."""
    
    # Console settings
    console_width: int = 100        # Width used by Console(width=...) universally
    
    # Currency and display
    currency_denom: str = "X"       # Default denomination symbol
    currency_precision: int = 2     # Decimal places for currency values
    
    # HTML export settings
    html_inline_styles: bool = True # Whether to inline CSS styles in HTML export
    
    # Table display settings
    balance_table_width: int = 80   # Width for balance sheet tables
    event_panel_width: int = 90     # Width for event panels
    
    # Formatting thresholds
    zero_threshold: float = 0.01    # Values below this are considered zero
    
    # Event display settings
    max_event_lines: int = 10       # Maximum lines per event in display
    show_event_icons: bool = True   # Whether to show emoji icons for events
    
    # Phase colors (for Rich console)
    phase_colors: dict = None
    
    def __post_init__(self):
        """Initialize mutable defaults."""
        if self.phase_colors is None:
            # Use object.__setattr__ to set value on frozen dataclass
            object.__setattr__(self, 'phase_colors', {
                'A': 'cyan',
                'B': 'yellow', 
                'C': 'green'
            })


# Global default settings instance
DEFAULT_SETTINGS = Settings()