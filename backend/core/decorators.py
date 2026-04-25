"""
Reusable decorators for common functionality.
"""

import time
import functools
from typing import Callable, Any
from core.exceptions import AIServiceError


def retry_with_fallback(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0, fallback_fn: Callable = None):
    """
    Retry decorator with exponential backoff and optional fallback.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each attempt
        fallback_fn: Function to call if all retries fail
    
    Usage:
        @retry_with_fallback(max_attempts=3, fallback_fn=use_cache)
        def call_api():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    print(f"[RETRY] Attempt {attempt}/{max_attempts} failed: {str(e)}")
                    
                    if attempt < max_attempts:
                        print(f"[RETRY] Retrying in {current_delay}s...")
                        time.sleep(current_delay)
                        current_delay *= backoff
            
            # All retries failed
            print(f"[RETRY] All {max_attempts} attempts failed")
            
            if fallback_fn:
                print("[FALLBACK] Using fallback function")
                try:
                    return fallback_fn(*args, **kwargs)
                except Exception as fallback_error:
                    print(f"[FALLBACK] Fallback also failed: {str(fallback_error)}")
            
            raise AIServiceError(
                f"Operation failed after {max_attempts} attempts",
                original_error=last_exception
            )
        
        return wrapper
    return decorator


def log_execution(func: Callable) -> Callable:
    """
    Log function execution time and parameters.
    
    Usage:
        @log_execution
        def process_text(text):
            ...
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        func_name = func.__name__
        print(f"[EXEC] Starting {func_name}")
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            print(f"[EXEC] {func_name} completed in {elapsed:.2f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"[EXEC] {func_name} failed after {elapsed:.2f}s: {str(e)}")
            raise
    
    return wrapper


def validate_input(**validators):
    """
    Validate function inputs using provided validator functions.
    
    Usage:
        @validate_input(text=lambda x: len(x) > 0, lang=lambda x: x in VALID_LANGS)
        def translate(text, lang):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Get function signature
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate each parameter
            for param_name, validator_fn in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if not validator_fn(value):
                        from core.exceptions import ValidationError
                        raise ValidationError(f"Invalid value for parameter '{param_name}'")
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator
