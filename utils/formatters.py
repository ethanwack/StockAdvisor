"""Formatting utilities - Format numbers and data for display"""

from typing import Union


def format_currency(value: Union[int, float], symbol: str = "$") -> str:
    """Format number as currency"""
    if isinstance(value, (int, float)):
        return f"{symbol}{value:,.2f}"
    return str(value)


def format_percent(value: Union[int, float], decimals: int = 2) -> str:
    """Format number as percentage"""
    if isinstance(value, (int, float)):
        return f"{value:.{decimals}f}%"
    return str(value)


def format_large_number(value: Union[int, float]) -> str:
    """Format large numbers with K, M, B notation"""
    if not isinstance(value, (int, float)) or value == 0:
        return str(value)
    
    if abs(value) >= 1e9:
        return f"{value/1e9:.2f}B"
    elif abs(value) >= 1e6:
        return f"{value/1e6:.2f}M"
    elif abs(value) >= 1e3:
        return f"{value/1e3:.2f}K"
    else:
        return f"{value:.2f}"


def format_ratio(value: Union[int, float], decimals: int = 2) -> str:
    """Format decimal ratio"""
    if isinstance(value, (int, float)):
        return f"{value:.{decimals}f}"
    return str(value)
