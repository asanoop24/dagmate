import importlib
import os
from plistlib import InvalidFileException
from types import ModuleType
from typing import Any, Dict

import yaml


def import_module_from_file(file_path: str) -> ModuleType:

    module_name = os.path.basename(file_path)[:-3]
    spec = importlib.util.spec_from_file_location(name=module_name, location=file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def import_module_from_package(package: str) -> ModuleType:
    
    module_name = os.path.basename(package)
    module = importlib.import_module(module_name, package)

    return module


def validate_file_location(filepath: str) -> None:
    """
    Validates if a given file path exists.
    An exception is thrown in case it doesn't.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"dagger could not find the file {filepath}")


def load_yaml(filepath: str) -> Dict[str, Any]:
    """
    Loads YAML config file to dictionary

    :returns: dict from YAML config file
    """
    # pylint: disable=consider-using-with
    try:
        config = yaml.load(
            stream=open(filepath, "r", encoding="utf-8"),
            Loader=yaml.FullLoader,
        )
    except Exception as err:
        raise InvalidFileException(f"Invalid yaml file {filepath}") from err
    return config
