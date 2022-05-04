from dagster import GraphDefinition, get_dagster_logger

_logger = get_dagster_logger()

from importlib import import_module

from apml.pipelines.utils import create_op_from_module
from apml.preprocessing import __all__ as _modules
from apml.preprocessing.__conf__ import inputs, outputs

PROJECT_NAME = "apml"
PIPELINE_NAME = "preprocessing"

_n_modules = len(_modules)

_ops = []
_deps = {}
for _name in _modules:
    if _name == "__conf__":
        continue

    # importing the module and saving it into a variable _mod
    _module = import_module(f"{PROJECT_NAME}.{PIPELINE_NAME}.{_name}")

    _op, _dep = create_op_from_module(_name, _module, inputs, outputs)
    _ops.append(_op)
    _deps[_name] = _dep


_ = GraphDefinition(name=PIPELINE_NAME, node_defs=_ops, dependencies=_deps).to_job()
