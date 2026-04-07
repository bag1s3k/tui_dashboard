import json
import logging
from typing import Any, Self
from copy import deepcopy

from utils.correct_path import get_path
from utils.datatypes import ValidatedPath
from utils.constants import CONFIGFILE_PATH
from models.decorator import Decorators

logger = logging.getLogger(__name__)

class AppConfig(Decorators):
    def __init__(self, path: ValidatedPath = get_path(CONFIGFILE_PATH)):
        super().__init__()

        self.path: ValidatedPath = path
        self.config: dict = {}
        self.saved_config: dict = {}

        self.read_config(path)

    @property
    def change(self):
        """Alias to variable '_change' in Decorators"""
        return self.config

    @property
    def saved_changes(self):
        """Alias to variable '_saved_changes' in Decorators"""
        return self.saved_config

    @Decorators.return_self
    def read_config(self, path: ValidatedPath = get_path(CONFIGFILE_PATH)) -> Self:
        """Load config from JSON file, also possible to change it during run"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.loads(f.read())
        except json.JSONDecodeError:
            logger.error(f"Error loading JSON file")
            return

        self.path = path
        self.config = data
        self.saved_config = deepcopy(self.config)
        logger.info("Config set on path: %s", path)

    @Decorators.return_self
    @Decorators.current_changes_trigger
    def add_new_setting(self, key: str, value: Any) -> Self:
        """Add new setting to config """
        if key in self.config.keys():
            logger.error("Key '%s' is already exists", key)
            return

        self.config[key] = value

    @Decorators.return_self
    @Decorators.current_changes_trigger
    def remove_setting(self, key: str) -> Self:
        """Remove setting from config"""
        if key not in self.config.keys():
            logger.error("Key '%s' not in config", key)
            return

        del self.config[key]

    @Decorators.return_self
    @Decorators.current_changes_trigger
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
            if value is None:
                logger.warning("Value for '%s' cannot be None", key)
                return
            self.config[key] = value


    @Decorators.return_self
    def save_config(self, path: ValidatedPath = None) -> Self:
        """Save config in JSON"""
        export_path = self.path if path is None else path

        try:
            with open(str(export_path), "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except (TypeError, OSError):
            logger.error("Failed to save config")

        self.saved_config = deepcopy(self.config)

appconfig = AppConfig()
