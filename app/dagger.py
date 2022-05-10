import inspect
from importlib import import_module
from types import ModuleType
from typing import Dict, List, Tuple, Union

import yaml
from dagster import (
    DependencyDefinition,
    GraphDefinition,
    In,
    JobDefinition,
    MultiDependencyDefinition,
    NodeInvocation,
    Nothing,
    OpDefinition,
    Out,
    get_dagster_logger,
    op,
    repository,
)
from matplotlib.pyplot import get

_logger = get_dagster_logger()


class Dagger:
    def __init__(self, config: Union[Dict, str]):
        self._conf = yaml.load(open(config), yaml.Loader) if isinstance(config, str) else config
        self._ins = {}
        self._outs = {}
        self._deps = {}
        self._deps = {}
        self._modules = {}
        self._step_fns = {}
        self._repos = {}

        self._mainframe = None
        self._main = None

    def activate(self):
        # frame and module from which the activate function is being called
        # ideally this would be the file passed as an arg to dagit -f <file> command
        self._mainframe = inspect.stack()[1][0]
        self._main = inspect.getmodule(self._mainframe)

        self._ins = self._build_input_defs()
        self._outs = self._build_output_defs()
        self._step_fns = self._load_modules()
        self._deps = self._build_dependency_defs()

        self._ops = self._build_op_defs(self._ins, self._outs, self._step_fns)
        self._graphs = self._build_graph_defs(self._ops, self._deps)
        self._jobs = self._build_job_defs(self._graphs)

        self._repos = self._build_repository_defs(self._jobs)

    def _build_input_defs(self) -> Dict:

        """
        builds input definitions for the op
        """

        _conf = self._conf
        _ins = {
            _workflow["name"]: {
                _step["name"]: {
                    _input["name"]: In() if _input["type"] == "var" else In(Nothing)
                    for _input in _step["input"]
                }
                if _step["input"] is not None
                else {}
                for _step in _workflow["steps"]
            }
            for _workflow in _conf["workflows"]
        }

        return _ins

    def _build_output_defs(self) -> Dict:

        _conf = self._conf
        _outs = {
            _workflow["name"]: {
                _step["name"]: {_output: Out() for _output in _step["output"]}
                if _step["output"] is not None
                else {"result": Out()}
                for _step in _workflow["steps"]
            }
            for _workflow in _conf["workflows"]
        }

        return _outs

    def _load_modules(self) -> Dict:

        _conf = self._conf
        _modules = {
            _workflow["name"]: {
                _step["name"]: import_module(
                    f'{_conf["project"]}.{_workflow["name"]}.{_step["name"]}'
                )
                for _step in _workflow["steps"]
            }
            for _workflow in _conf["workflows"]
        }

        _step_fns = {}
        for _workflow in _conf["workflows"]:
            _step_fns[_workflow["name"]] = {}
            for _step in _workflow["steps"]:
                _step_fn = (
                    _modules[_workflow["name"]][_step["name"]].step_fn
                    if "step_fn" in dir(_modules[_workflow["name"]][_step["name"]])
                    else None
                )
                _step_fn.__qualname__ = _step["name"]
                _step_fn.__name__ = _step["name"]
                _step_fns[_workflow["name"]][_step["name"]] = _step_fn

        return _step_fns

    def _build_op_defs(
        self, input_defs: Dict, output_defs: Dict, step_fns: Dict
    ) -> Tuple[OpDefinition, Dict[str, DependencyDefinition]]:

        _conf = self._conf
        _step_fns = step_fns
        _ins = input_defs
        _outs = output_defs

        _ops = {
            _workflow["name"]: {
                _step["name"]: op(
                    f'__{_workflow["name"]}__{_step["name"]}',
                    ins=_ins[_workflow["name"]][_step["name"]],
                    out=_outs[_workflow["name"]][_step["name"]],
                )(_step_fns[_workflow["name"]][_step["name"]])
                for _step in _workflow["steps"]
            }
            for _workflow in _conf["workflows"]
        }

        return _ops

    def _build_dependency_defs(self) -> Dict:

        _conf = self._conf

        _deps = {
            _workflow["name"]: {
                NodeInvocation(f'__{_workflow["name"]}__{_step["name"]}', _step["name"]): {
                    _input["name"]: DependencyDefinition(
                        _input["source"]["step"], _input["source"]["var"]
                    )
                    if _input["type"] == "var"
                    else MultiDependencyDefinition(
                        [DependencyDefinition(x, "result") for x in _input["source"]["step"]]
                    )
                    for _input in _step["input"]
                }
                if _step["input"] is not None
                else {}
                for _step in _workflow["steps"]
            }
            for _workflow in _conf["workflows"]
        }

        return _deps

    def _build_graph_defs(self, op_defs: Dict, dep_defs: Dict):

        _conf = self._conf
        _ops = op_defs
        _deps = dep_defs

        _graphs = {
            _workflow["name"]: GraphDefinition(
                name=_workflow["name"],
                node_defs=list(_ops[_workflow["name"]].values()),
                dependencies=_deps[_workflow["name"]],
            )
            for _workflow in _conf["workflows"]
        }

        return _graphs

    def _build_job_defs(self, graph_defs: Dict):

        _conf = self._conf
        _graphs = graph_defs

        _jobs = {
            _workflow["name"]: _graphs[_workflow["name"]].to_job()
            for _workflow in _conf["workflows"]
        }

        return _jobs

    # def _build_schedule_defs(config: Dict, graph_defs: Dict):

    #     _conf = config
    #     _graphs = graph_defs

    #     _jobs = {
    #         _workflow["name"]: _graphs[_workflow["name"]].to_job() for _workflow in _conf["workflows"]
    #     }

    #     return _jobs

    def _build_repository_defs(self, job_defs: Dict[str, JobDefinition]):

        _conf = self._conf
        _jobs = job_defs

        _repos = {}
        # _g = globals()
        for _workflow in _conf["workflows"]:

            @repository(name=_workflow["name"])
            def _repo():
                return [_jobs[_workflow["name"]]]

            _repo.__name__ = _workflow["name"]
            _repo.__qualname__ = _workflow["name"]

            # _g[f'__repository__{_workflow["name"]}'] = _repo
            _repos[_workflow["name"]] = _repo

            self._mainframe.f_globals[f'__repository__{_workflow["name"]}'] = _repo
            setattr(self._main, f'__repository__{_workflow["name"]}', _repo)

        return _repos
