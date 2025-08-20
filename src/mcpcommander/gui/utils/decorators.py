"""GUI utility decorators."""

import functools
import time
from typing import Callable, Any
from PySide6.QtCore import QTimer


def debounce(wait_ms: int) -> Callable:
    """Debounce decorator for GUI functions."""
    def decorator(func: Callable) -> Callable:
        timer = None
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            nonlocal timer
            
            def call_func():
                func(*args, **kwargs)
            
            if timer is not None:
                timer.stop()
                timer.deleteLater()
            
            timer = QTimer()
            timer.timeout.connect(call_func)
            timer.setSingleShot(True)
            timer.start(wait_ms)
            
        return wrapper
    return decorator


def throttle(wait_ms: int) -> Callable:
    """Throttle decorator for GUI functions."""
    def decorator(func: Callable) -> Callable:
        last_called = 0
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            nonlocal last_called
            now = time.time() * 1000
            
            if now - last_called >= wait_ms:
                last_called = now
                return func(*args, **kwargs)
            
        return wrapper
    return decorator