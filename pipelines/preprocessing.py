from dagster import get_dagster_logger, GraphDefinition
_logger = get_dagster_logger()

from importlib import import_module

from apml.preprocessing import __all__ as _modules
from apml.preprocessing.config import in_args, out_args

from apml.pipelines.utils import create_dynamic_op


# _modules = preprocessing.__all__
_n_modules = len(_modules)
_project_name = "apml"
_pipeline_name = "preprocessing"

_ops = []
_deps = {}
for _name in _modules:
    if _name == "config": continue

    # importing the module and saving it into a variable _mod
    _module = import_module(f"{_project_name}.{_pipeline_name}.{_name}")

    _op, _dep = create_dynamic_op(_name, _module, in_args, out_args)
    _ops.append(_op)
    _deps[_name] = _dep


_ = GraphDefinition(
    name="preprocessing",
    node_defs=_ops,
    dependencies=_deps
).to_job()