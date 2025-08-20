"""Async Qt utilities for GUI operations."""

from typing import Any, Callable, Optional
from PySide6.QtCore import QObject, QThread, Signal


class AsyncQtWorker(QObject):
    """Generic async worker for Qt operations."""
    
    # Signals
    finished = Signal()
    result = Signal(object)
    error = Signal(str)
    progress = Signal(int)
    
    def __init__(self, func: Callable, *args, **kwargs) -> None:
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self) -> None:
        """Execute the function."""
        try:
            result = self.func(*self.args, **self.kwargs)
            self.result.emit(result)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()


def run_async(func: Callable, *args, **kwargs) -> tuple[QThread, AsyncQtWorker]:
    """Run function asynchronously in Qt thread."""
    thread = QThread()
    worker = AsyncQtWorker(func, *args, **kwargs)
    worker.moveToThread(thread)
    
    thread.started.connect(worker.run)
    worker.finished.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)
    
    return thread, worker