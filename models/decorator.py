from functools import wraps
from deepdiff import DeepDiff
from typing import Any, Self
import logging
from copy import deepcopy

logger = logging.getLogger(__name__)

class Chain:
    @classmethod
    def return_self(cls, func):
        """Decorator that automatically return self"""

        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Self:
            func(self, *args, **kwargs)
            return self

        return wrapper

class Changes:
    def __init__(self):
        self._change: Any = None
        self._saved_changes: Any = None

    @property
    def change(self) -> Any:
        return self._change

    @property
    def unsaved_changes(self):
        saved_copy = deepcopy(self._saved_changes)
        current_copy = deepcopy(self._change)
        return DeepDiff(saved_copy, current_copy)

    @classmethod
    def current_changes_trigger(cls, func):
        """Decorator that automatically sets current unsaved changes"""

        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            before = deepcopy(self.change)
            result = func(self, *args, **kwargs)
            after = deepcopy(self.change)

            diff = DeepDiff(before, after)
            if diff:
                logger.info(f"Changes detected: {str(diff)[1:-1]}")

            return result
        return wrapper

class Decorators(Chain, Changes):
    pass
