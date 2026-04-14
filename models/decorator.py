from functools import wraps
from deepdiff import DeepDiff
from typing import Any, Self
import logging
from copy import deepcopy

logger = logging.getLogger(__name__)

def return_self(func):
    """Decorator that automatically return self"""

    @wraps(func)
    def wrapper(self, *args, **kwargs) -> Self:
        func(self, *args, **kwargs)
        return self

    return wrapper

def current_changes_trigger(func):
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