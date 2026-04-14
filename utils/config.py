import json
import logging
from typing import Any, Self
from copy import deepcopy

from deepdiff import DeepDiff

from utils.correct_path import get_path
from utils.datatypes import ValidatedPath
from utils.constants import CONFIGFILE_PATH
from models.decorator import return_self, current_changes_trigger


logger = logging.getLogger(__name__)

class AppConfig:
    #TODO: 1. don't always return Self, return current pointer
        # instead: add_new_setting("nested.option").add_new_setting("nested.another")
        # this: add_new_setting("nested.option").add_new_setting("another")
        #? Explanation:
            # after we added the first setting pointer moved so no need to write 'nested again'
    #TODO: 2. Instead explicit save config method, methods could have argument 'inplace'

    def __init__(self, path: ValidatedPath = get_path(CONFIGFILE_PATH)):
        self.path: ValidatedPath = path
        self.config: dict = {}
        self.saved_config: dict = {}
        self.read_config(path)

    @property
    def change(self):
        """Alias to variable '_change' in Decorators"""
        return self.config

    @property
    def unsaved_changes(self):
        """Returns current unsaved changes"""
        return DeepDiff(self.saved_config, self.config)

    def _locate(self, key_path: str, edit: bool = False) -> tuple:
        """Access config via dots and it also allows to interact with nested config"""
        keys = key_path.split(".")
        target = self.config
        for k in keys[:-1]:
            if k not in target or not isinstance(target[k], dict):
                if edit:
                    target[k] = {}
                else:
                    logger.error("Key: '%s' doesn't exist", k)
            target = target[k]
        return target, keys[-1]

    @return_self
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

    @return_self
    @current_changes_trigger
    def add_new_setting(self, key_path: str, value: Any) -> Self:
        """Add new setting to config """
        parent, key = self._locate(key_path, edit=True)
        if key in parent.keys():
            logger.error("Key is already exists: %s", key)
            return

        parent[key] = value

    @return_self
    @current_changes_trigger
    def remove_setting(self, key: str) -> Self:
        """Remove setting from config"""
        parent, key = self._locate(key)
        if key not in parent.keys():
            logger.error("Key '%s' not in config", key)
            return

        del parent[key]

    @return_self
    @current_changes_trigger
    def change_setting(self, key_path: str, value: Any = None, new_key_path: str = None) -> Self:
        """Change setting in config"""
        parent, key = self._locate(key_path)
        if key not in parent.keys():
            logger.error("Key '%s' not in config", key)
            return

        if new_key_path:
            parent, new_key = self._locate(new_key_path, edit=True)
            new_value = value if value else parent[key]
            parent[new_key] = new_value
            del_parent, del_key = self._locate(key)
            del del_parent[del_key]
        else:
            parent, key = self._locate(key_path)
            if value is None:
                logger.warning("Value for '%s' cannot be None", key)
                return
            parent[key] = value

    @return_self
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
