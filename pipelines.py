from dagster import GraphDefinition, get_dagster_logger

_logger = get_dagster_logger()

import os
from importlib import import_module

from .utils import create_op_from_module

PROJECT_NAME = "apml"


_pipelines = [f for f in os.listdir(".") if os.path.isdir(f) and "__conf__.py" in os.listdir(f)]

for _pipeline in _pipelines:
    _conf = import_module(f"{PROJECT_NAME}.{_pipeline}.__conf__")
    _modules = _conf.steps
    _inputs = _conf.inputs
    _outputs = _conf.outputs

    _ops = []
    _deps = {}
    for _name in _modules:
        if _name == "__conf__":
            continue

        # importing the module and saving it into a variable _mod
        _module = import_module(f"{PROJECT_NAME}.{_pipeline}.{_name}")

        _op, _dep = create_op_from_module(_name, _module, _inputs, _outputs)
        _ops.append(_op)
        _deps[_name] = _dep

    _ = GraphDefinition(name=_pipeline, node_defs=_ops, dependencies=_deps).to_job()
