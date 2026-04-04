import json
import logging
import functools
from typing import Any
from deepdiff import DeepDiff

from utils.correct_path import get_path
from utils.datatypes import ValidatedPath
from utils.constants import CONFIGFILE_PATH

logger = logging.getLogger(__name__)

class AppConfig:
    def __init__(self, path: ValidatedPath = get_path(CONFIGFILE_PATH)):
        self.path: ValidatedPath = None
        self.config: dict = None
        self.unsaved_config: dict = None

        self.read_config(path)

    class _Decorators(object):
        @classmethod
        def unsaved_trigger(cls, func):
            """Decorator to automatically set unsaved config"""
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                config_before = self.config.copy()
                result = func(self, *args, **kwargs)
                config_after = self.config

                self.unsaved_config = DeepDiff(config_before, config_after)

                return result
            return wrapper

    def read_config(self, path: ValidatedPath = get_path(CONFIGFILE_PATH)) -> dict:
        """Load config from JSON file, also possible to change it during run"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.loads(f.read())
        except json.JSONDecodeError:
            logger.error("Wrong input from JSON file")
            return self.config

        self.path = path
        self.config = data
        logger.info("Config set on path: %s", path)
        return self.config

    @_Decorators.unsaved_trigger
    def add_new_setting(self, key: str, value: Any) -> dict:
        """Add new setting to config """
        if key in self.config.keys():
            logger.error("Key '%s' is already exists", key)
            return self.config

        self.config[key] = value
        logger.info("New setting '%s' has been added", {key: value})
        return self.config

    @_Decorators.unsaved_trigger
    def remove_setting(self, key: str) -> dict:
        """Remove setting from config"""
        if key not in self.config.keys():
            logger.error("Key '%s' not in config", key)
            return self.config

        del self.config[key]
        logger.info("Setting '%s' has been deleted", key)
        return self.config

    @_Decorators.unsaved_trigger
    def change_setting(self, key: str, value: Any = None, new_key: str = None) -> dict:
        """Change setting in config"""
        if key not in self.config.keys():
            logger.error("Key '%s' not in config", key)
            return self.config
        if new_key:
            new_value = value if value else self.config[key]
            self.config[new_key] = new_value
            del self.config[key]
            logger.info("Key '%s' has been changed to '%s'", key, new_key)
        else:
            if not value:
                logger.warning("Value '%s' cannot be None", key)
                return self.config
            self.config[key] = value
            logger.info("'%s' has been changed to '%s'", key, value)

        return self.config

    def save_config(self, path: ValidatedPath = None) -> dict:
        """Save config in JSON"""
        export_path = self.path if path is None else path

        try:
            with open(str(export_path), "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except json.JSONDecodeError:
            logger.error("Wrong data to save")
            return self.config

        self.unsaved_config = {}
        return self.config

appconfig = AppConfig()