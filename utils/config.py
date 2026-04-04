import json
import logging
import functools
from typing import Any, Self
from deepdiff import DeepDiff

from utils.correct_path import get_path
from utils.datatypes import ValidatedPath
from utils.constants import CONFIGFILE_PATH

logger = logging.getLogger(__name__)

class AppConfig:
    def __init__(self, path: ValidatedPath = get_path(CONFIGFILE_PATH)):
        self.path: ValidatedPath = None
        self.config: dict = None
        self.saved_config: dict = None

        self.read_config(path)

    @property
    def unsaved_config(self):
        import copy

        saved_copy = copy.deepcopy(self.saved_config)
        current_copy = copy.deepcopy(self.config)
        return DeepDiff(saved_copy, current_copy)

    class _Decorators(object):
        @classmethod
        def current_changes_trigger(cls, func):
            """Decorator that automatically sets unsaved config"""
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs) -> Any:
                from copy import deepcopy

                config_before = deepcopy(self.config)
                result = func(self, *args, **kwargs)
                config_after = deepcopy(self.config)

                diff = DeepDiff(config_before, config_after)
                if diff:
                    logger.info(str(diff)[1:-1])

                return result
            return wrapper

        @classmethod
        def return_config(cls, func):
            """Decorator that automatically return self"""
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs) -> Self:
                func(self, *args, **kwargs)
                return self
            return wrapper

    @_Decorators.return_config
    def read_config(self, path: ValidatedPath = get_path(CONFIGFILE_PATH)) -> Self:
        """Load config from JSON file, also possible to change it during run"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.loads(f.read())
        except json.JSONDecodeError:
            logger.error("Wrong input from JSON file")
            return

        self.path = path
        self.config = data
        self.saved_config = self.config.copy()
        logger.info("Config set on path: %s", path)

    @_Decorators.return_config
    @_Decorators.current_changes_trigger
    def add_new_setting(self, key: str, value: Any) -> Self:
        """Add new setting to config """
        if key in self.config.keys():
            logger.error("Key '%s' is already exists", key)
            return

        self.config[key] = value

    @_Decorators.return_config
    @_Decorators.current_changes_trigger
    def remove_setting(self, key: str) -> Self:
        """Remove setting from config"""
        if key not in self.config.keys():
            logger.error("Key '%s' not in config", key)
            return

        del self.config[key]

    @_Decorators.return_config
    @_Decorators.current_changes_trigger
    def change_setting(self, key: str, value: Any = None, new_key: str = None) -> Self:
        """Change setting in config"""
        if key not in self.config.keys():
            logger.error("Key '%s' not in config", key)
            return
        if new_key:
            new_value = value if value else self.config[key]
            self.config[new_key] = new_value
            del self.config[key]
        else:
            if not value:
                logger.warning("Value '%s' cannot be None", key)
                return
            self.config[key] = value


    @_Decorators.return_config
    def save_config(self, path: ValidatedPath = None) -> Self:
        """Save config in JSON"""
        export_path = self.path if path is None else path

        try:
            with open(str(export_path), "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except json.JSONDecodeError:
            logger.error("Wrong data to save")

        self.saved_config = self.config.copy()

appconfig = AppConfig()