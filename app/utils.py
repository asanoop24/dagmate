import importlib
import os
from types import ModuleType


def import_module_from_file(module_path: str) -> ModuleType:

    module_name = os.path.basename(module_path)[:-3]
    spec = importlib.util.spec_from_file_location(name=module_name, location=module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module
