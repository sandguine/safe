"""
Domain-specific exceptions and error handling for oversight curriculum.
Provides custom exceptions and retry/back-off mechanisms for robust execution.
"""

import time
import logging
from functools import wraps
from typing import Type, Callable, Any, Optional, Union
import httpx


class OversightError(Exception):
    """Base exception for oversight curriculum"""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self):
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


class ConfigurationError(OversightError):
    """Raised when configuration is invalid or missing"""
    pass


class ModelError(OversightError):
    """Raised when model API calls fail"""
    pass


class SafetyViolation(OversightError):
    """Raised when safety checks fail"""
    pass


class QuotaExceeded(OversightError):
    """Raised when API quota is exceeded"""
    pass


class ValidationError(OversightError):
    """Raised when validation fails"""
    pass


class MetricsError(OversightError):
    """Raised when metrics collection fails"""
    pass


class OutputError(OversightError):
    """Raised when output operations fail"""
    pass


class CostLimitExceeded(OversightError):
    """Raised when cost limits are exceeded"""
    pass


# Error mapping for API exceptions
API_ERROR_MAPPING = {
    httpx.TimeoutException: QuotaExceeded,
    httpx.HTTPStatusError: ModelError,
    httpx.ConnectError: ModelError,
    httpx.RequestError: ModelError,
}


def map_api_exception(exc: Exception, context: str = "") -> OversightError:
    """Map API exceptions to domain-specific exceptions"""
    exc_type = type(exc)
    
    if exc_type in API_ERROR_MAPPING:
        domain_exc_class = API_ERROR_MAPPING[exc_type]
        message = f"API error in {context}: {str(exc)}"
        return domain_exc_class(message, {"original_exception": str(exc)})
    
    # Default mapping
    return ModelError(f"Unexpected API error in {context}: {str(exc)}")


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (Exception,),
    logger: Optional[logging.Logger] = None
):
    """
    Decorator that implements exponential back-off retry logic.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        exponential_base: Base for exponential back-off
        exceptions: Tuple of exceptions to catch and retry
        logger: Logger instance for retry logging
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exception = exc
                    
                    if attempt == max_retries:
                        # Final attempt failed, re-raise the exception
                        if logger:
                            logger.error(
                                f"Function {func.__name__} failed after "
                                f"{max_retries + 1} attempts. "
                                f"Last error: {str(exc)}"
                            )
                        raise
                    
                    # Calculate delay with exponential back-off
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )
                    
                    if logger:
                        logger.warning(
                            f"Function {func.__name__} failed (attempt "
                            f"{attempt + 1}/{max_retries + 1}). "
                            f"Retrying in {delay:.2f}s. Error: {str(exc)}"
                        )
                    
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator


def safe_api_call(
    context: str = "",
    max_retries: int = 3,
    logger: Optional[logging.Logger] = None
):
    """
    Decorator for safe API calls with automatic exception mapping.
    
    Args:
        context: Context string for error messages
        max_retries: Maximum number of retry attempts
        logger: Logger instance for error logging
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                # Map to domain-specific exception
                domain_exc = map_api_exception(exc, context)
                
                if logger:
                    logger.error(
                        f"API call failed in {context}: {str(exc)} -> "
                        f"{type(domain_exc).__name__}"
                    )
                
                raise domain_exc
        
        return wrapper
    return decorator


class ErrorHandler:
    """Centralized error handling and logging"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.error_count = 0
        self.error_history = []
    
    def handle_error(
        self, 
        error: Exception, 
        context: str = "",
        reraise: bool = True
    ) -> None:
        """
        Handle an error with logging and optional re-raising.
        
        Args:
            error: The exception to handle
            context: Context string for logging
            reraise: Whether to re-raise the error after handling
        """
        self.error_count += 1
        
        # Log the error
        self.logger.error(
            f"Error in {context}: {type(error).__name__}: {str(error)}"
        )
        
        # Store in history
        self.error_history.append({
            "timestamp": time.time(),
            "context": context,
            "error_type": type(error).__name__,
            "error_message": str(error)
        })
        
        if reraise:
            raise error
    
    def get_error_summary(self) -> dict:
        """Get a summary of all errors encountered"""
        return {
            "total_errors": self.error_count,
            "error_history": self.error_history,
            "error_types": {
                error["error_type"]: len([
                    e for e in self.error_history 
                    if e["error_type"] == error["error_type"]
                ])
                for error in self.error_history
            }
        }
    
    def clear_history(self) -> None:
        """Clear error history"""
        self.error_history.clear()
        self.error_count = 0


# Global error handler instance
_global_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler


def set_error_handler(handler: ErrorHandler) -> None:
    """Set the global error handler instance"""
    global _global_error_handler
    _global_error_handler = handler


# Convenience functions for common error patterns
def handle_api_error(func: Callable) -> Callable:
    """Decorator for handling API errors with automatic mapping"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            domain_exc = map_api_exception(exc, func.__name__)
            get_error_handler().handle_error(domain_exc, func.__name__)
            raise domain_exc
    return wrapper


def handle_safety_violation(func: Callable) -> Callable:
    """Decorator for handling safety violations"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SafetyViolation as exc:
            get_error_handler().handle_error(exc, func.__name__)
            raise
        except Exception as exc:
            # Convert unexpected errors to safety violations if appropriate
            if "safety" in str(exc).lower() or "harm" in str(exc).lower():
                safety_exc = SafetyViolation(
                    f"Safety violation in {func.__name__}: {str(exc)}"
                )
                get_error_handler().handle_error(safety_exc, func.__name__)
                raise safety_exc
            raise
    return wrapper


def handle_cost_limit(func: Callable) -> Callable:
    """Decorator for handling cost limit violations"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CostLimitExceeded as exc:
            get_error_handler().handle_error(exc, func.__name__)
            raise
        except Exception as exc:
            # Convert cost-related errors
            if "cost" in str(exc).lower() or "quota" in str(exc).lower():
                cost_exc = CostLimitExceeded(
                    f"Cost limit exceeded in {func.__name__}: {str(exc)}"
                )
                get_error_handler().handle_error(cost_exc, func.__name__)
                raise cost_exc
            raise
    return wrapper 