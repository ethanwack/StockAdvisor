"""
Centralized Validators
Common validation logic for all services
"""

from typing import Optional, List
import re
from datetime import datetime


class ValidationError(Exception):
    """Custom validation error"""
    pass


def validate_symbol(symbol: str) -> bool:
    """
    Validate stock symbol format
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        True if valid, raises ValidationError otherwise
    """
    if not symbol:
        raise ValidationError("Symbol cannot be empty")
    
    if not re.match(r"^[A-Z]{1,5}$", symbol.strip().upper()):
        raise ValidationError(f"Invalid symbol format: {symbol}")
    
    return True


def validate_price(price: float) -> bool:
    """
    Validate price value
    
    Args:
        price: Stock price
        
    Returns:
        True if valid, raises ValidationError otherwise
    """
    if price is None:
        raise ValidationError("Price cannot be None")
    
    if price < 0:
        raise ValidationError(f"Price cannot be negative: {price}")
    
    return True


def validate_date_range(start_date: datetime, end_date: datetime) -> bool:
    """
    Validate date range
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        True if valid, raises ValidationError otherwise
    """
    if start_date >= end_date:
        raise ValidationError(f"Start date {start_date} must be before end date {end_date}")
    
    return True


def validate_shares(shares: float) -> bool:
    """
    Validate share quantity
    
    Args:
        shares: Number of shares
        
    Returns:
        True if valid, raises ValidationError otherwise
    """
    if shares is None:
        raise ValidationError("Shares cannot be None")
    
    if shares <= 0:
        raise ValidationError(f"Shares must be positive: {shares}")
    
    return True


def validate_percentage(value: float, min_val: float = 0.0, max_val: float = 100.0) -> bool:
    """
    Validate percentage value
    
    Args:
        value: Percentage value
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        True if valid, raises ValidationError otherwise
    """
    if value is None:
        raise ValidationError("Percentage cannot be None")
    
    if value < min_val or value > max_val:
        raise ValidationError(f"Percentage {value} out of range [{min_val}, {max_val}]")
    
    return True


def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email address
        
    Returns:
        True if valid, raises ValidationError otherwise
    """
    if not email:
        raise ValidationError("Email cannot be empty")
    
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        raise ValidationError(f"Invalid email format: {email}")
    
    return True


def validate_symbols_list(symbols: List[str]) -> bool:
    """
    Validate list of symbols
    
    Args:
        symbols: List of stock symbols
        
    Returns:
        True if valid, raises ValidationError otherwise
    """
    if not symbols:
        raise ValidationError("Symbol list cannot be empty")
    
    if not isinstance(symbols, list):
        raise ValidationError("Symbols must be a list")
    
    for symbol in symbols:
        validate_symbol(symbol)
    
    return True


def safe_validate(validator_func, value, default: bool = False) -> bool:
    """
    Safely call a validator without raising exceptions
    
    Args:
        validator_func: Validator function to call
        value: Value to validate
        default: Default return value if validation fails
        
    Returns:
        True if valid, False otherwise
    """
    try:
        return validator_func(value)
    except ValidationError:
        return default
