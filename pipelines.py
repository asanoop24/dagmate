from dagster import GraphDefinition, get_dagster_logger, repository
from git import Repo

_logger = get_dagster_logger()

import os
from importlib import import_module

from apml.utils import create_op_from_module

PROJECT_NAME = "apml"


if __name__ == "__main__":

    _pipelines = [f for f in os.listdir(".") if os.path.isdir(f) and "__conf__.py" in os.listdir(f)]

    _jobs = []
    for _pipeline in _pipelines:

        # reading the configuration file for the pipeline and dependencies
        _conf = import_module(f"{PROJECT_NAME}.{_pipeline}.__conf__")
        _modules = _conf.steps
        _inputs = _conf.inputs
        _outputs = _conf.outputs

        _ops = []
        _deps = {}
        for _name in _modules:
            if _name == "__conf__":
                continue

            # importing the module that needs to be converted to the workflow step (op)
            _module = import_module(f"{PROJECT_NAME}.{_pipeline}.{_name}")

            # assigning a unique name to the op to prevent naming conflicts with other pipelines
            _uname = f"{_pipeline}__{_name}"

            # creating the op using the parameters defined
            _op, _dep = create_op_from_module(_name, _pipeline, _module, _inputs, _outputs)

            # appending op to the node_defs list that will be used during the job creation
            _ops.append(_op)

            # creating the dependency dictionary that will be used during the job creation
            _deps[_uname] = _dep

        # creating the job for the pipeline using the ops and dependencies generated above
        _job = GraphDefinition(name=_pipeline, node_defs=_ops, dependencies=_deps).to_job()
        _jobs.append(_job)

    @repository(name=PROJECT_NAME)
    def repo():
        return _jobs
