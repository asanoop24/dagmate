import inspect
import os
from pyclbr import Function
from types import ModuleType
from typing import Any, Dict, List, Tuple, Union

import yaml
from dagster import (
    DagsterType,
    DefaultScheduleStatus,
    DependencyDefinition,
    GraphDefinition,
    In,
    JobDefinition,
    MultiDependencyDefinition,
    NodeInvocation,
    Nothing,
    OpDefinition,
    Optional,
    Out,
    RepositoryDefinition,
    ScheduleDefinition,
    get_dagster_logger,
    op,
    repository,
)

from dagmate.utils import import_module_from_file, load_yaml, validate_file_location

_logger = get_dagster_logger()


VALID_YAML_OVERALL_ATTRIBUTES = ["project", "workflows"]
VALID_YAML_WORKFLOW_ATTRIBUTES = ["name", "steps", "schedule"]
VALID_YAML_STEP_ATTRIBUTES = ["name", "module", "function", "dependencies", "return"]
VALID_YAML_DEPENDENCY_ATTRIBUTES = ["type", "name", "source"]
VALID_YAML_SOURCE_ATTRIBUTES = ["step", "param"]


class Dagmate:
    """
    Takes a YAML config or a python dictionary and generates DAGs.
    :param config_filepath: the filepath of the DAG factory YAML config file.
        Must be absolute path to file. Cannot be used with `config`.
    :type config_file: str
    :param config: Dagmate config dictionary. Cannot be user with `config_file`.
    :type config: dict
    """

    def __init__(self, config_file: Optional[str] = None, config: Optional[dict] = None) -> None:

        assert bool(config_file) ^ bool(
            config
        ), "Either `config_file` or `config` should be provided"
        if config_file:
            validate_file_location(filepath=config_file)
            self.config: Dict[str, Any] = load_yaml(filepath=config_file)
        if config:
            self.config: Dict[str, Any] = config

    @staticmethod
    def _validate_config(config: str) -> None:
        """
        Validates config file path is absolute
        """
        if not os.path.exists(config):
            raise Exception("Dagmate `config` must be absolute path")

    def activate(self):
        """
        activates Dagmate and uses the loaded config to
            build input and output definitions for ops
            build op and dependency definitions from inputs and outputs
            build graph and job definitions
            build repository definitions from jobs
            load repositories in the globals() dict of the mainframe module
        """

        # frame and module from which the activate function is being called
        # ideally this would be the file passed as an arg to dagit -f <file> command
        self._mainframe = inspect.stack()[1][0]
        self._main = inspect.getmodule(self._mainframe)

        # building input params, output params, step functions and dependencies
        # required for ops, graphs and jobs
        self._build_input_defs()
        self._build_output_defs()
        self._load_modules()
        self._load_step_fns()  # depends on loaded modules
        self._build_dependency_defs()

        # building op definitions, graph definitions and job defnitions
        self._build_op_defs()  # depends on input_defs and output_defs
        self._build_graph_defs()  # depends on input_defs and output_defs
        self._build_job_defs()  # depends on input_defs and output_defs
        self._build_schedule_defs()  # depends on input_defs and output_defs

        # building repositories for each workflow
        self._build_repository_defs()

    def _build_input_defs(self) -> None:
        """
        builds input definitions for the op that are
        passed in @op decorator while defining the op

        :params
            self: Dagmate -> an instance of class Dagmate
        :returns
            _ins: Dict[str,Dict[str,Union[None,Dict[str,DagsterType]]]] ->
            a nested dictionary for input definitions for each op in each workflow
        """
        _conf = self.config
        _ins = {
            _workflow["name"]: {
                _step["name"]: {
                    _input["name"]: In() if _input["type"] == "param" else In(Nothing)
                    for _input in _step["dependencies"]
                }
                if _step["dependencies"] is not None
                else {}
                for _step in _workflow["steps"]
            }
            for _workflow in _conf["workflows"]
        }

        self.input_defs = _ins
        # return _ins

    def _build_output_defs(self) -> None:
        """
        builds output definitions for the op that are
        passed in @op decorator while defining the op

        :params
            self: Dagmate -> an instance of class Dagmate
        :returns
            _outs: Dict[str,Union[None,Dict[str,DagsterType]]] ->
            a nested dictionary for output definitions for each op in each workflow
        """
        _conf = self.config
        _outs = {
            _workflow["name"]: {
                _step["name"]: {_output: Out() for _output in _step["return"]}
                if _step["return"] is not None
                else {"result": Out()}
                for _step in _workflow["steps"]
            }
            for _workflow in _conf["workflows"]
        }

        self.output_defs = _outs
        # return _outs

    def _load_modules(self) -> None:
        """
        loads the module in which the function to be executed for
        the op resides

        :params
            self: Dagmate -> an instance of class Dagmate
        :returns
            _modules: Dict[str,Dict[str,ModuleType]] ->
            a nested dictionary for loaded modules for each op in each workflow
        """
        _conf = self.config

        _modules = {
            _workflow["name"]: {
                _step["name"]: import_module_from_file(f'{_step["module"]}')
                for _step in _workflow["steps"]
            }
            for _workflow in _conf["workflows"]
        }

        self.modules = _modules
        # return _modules

    def _load_step_fns(self) -> Dict[str, Dict[str, Function]]:
        """
        loads the module in which the function to be executed for
        the op resides

        :params
            self: Dagmate -> an instance of class Dagmate
        :returns
            _modules: Dict[str,Dict[str,ModuleType]] ->
            a nested dictionary for loaded modules for each op in each workflow
        """
        _conf = self.config
        _modules = self.modules

        _step_fns = {}
        for _workflow in _conf["workflows"]:
            _step_fns[_workflow["name"]] = {}
            for _step in _workflow["steps"]:
                _step_fn = getattr(_modules[_workflow["name"]][_step["name"]], _step["function"])
                _step_fn.__qualname__ = _step["name"]
                _step_fn.__name__ = _step["name"]
                _step_fns[_workflow["name"]][_step["name"]] = _step_fn

        self.step_fns = _step_fns
        # return _step_fns

    def _build_op_defs(self) -> None:
        """
        loads the module in which the function to be executed for
        the op resides

        :params
            self: Dagmate -> an instance of class Dagmate
        :returns
            _modules: Dict[str,Dict[str,ModuleType]] ->
            a nested dictionary for loaded modules for each op in each workflow
        """
        _conf = self.config
        _step_fns = self.step_fns
        _ins = self.input_defs
        _outs = self.output_defs

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

        self.op_defs = _ops
        # return _ops

    def _build_dependency_defs(self) -> Dict:
        """
        builds the dependency definitions and mapping of params between ops

        :params
            self: Dagmate -> an instance of class Dagmate
        :returns
            _modules: Dict[str,Dict[str,ModuleType]] ->
            a nested dictionary for dependency definitions for each op in each workflow
        """
        _conf = self.config

        _deps = {
            _workflow["name"]: {
                NodeInvocation(f'__{_workflow["name"]}__{_step["name"]}', _step["name"]): {
                    _input["name"]: DependencyDefinition(
                        _input["source"]["step"], _input["source"]["param"]
                    )
                    if _input["type"] == "param"
                    else MultiDependencyDefinition(
                        [
                            DependencyDefinition(
                                x, list(self.output_defs[_workflow["name"]][x].keys())[-1]
                            )
                            for x in _input["source"]["step"]
                        ]
                    )
                    for _input in _step["dependencies"]
                }
                if _step["dependencies"] is not None
                else {}
                for _step in _workflow["steps"]
            }
            for _workflow in _conf["workflows"]
        }

        self.dependency_defs: Dict = _deps
        # return _deps

    def _build_graph_defs(self) -> None:
        """
        builds the graph definitions with ops as nodes and dependencies as edges

        :params
            self: Dagmate -> an instance of class Dagmate
        :returns
            _modules: Dict[str,GraphDefinition] ->
            a dictionary for graph definitions for each job
        """
        _conf = self.config
        _ops = self.op_defs
        _deps = self.dependency_defs

        _graphs = {
            _workflow["name"]: GraphDefinition(
                name=_workflow["name"],
                node_defs=list(_ops[_workflow["name"]].values()),
                dependencies=_deps[_workflow["name"]],
            )
            for _workflow in _conf["workflows"]
        }

        self.graph_defs = _graphs
        # return _graphs

    def _build_job_defs(self):
        """
        builds the job definitions to be loaded into the repositories

        :params
            self: Dagmate -> an instance of class Dagmate
        :returns
            _modules: Dict[str,JobDefinition] ->
            a dictionary for jobs for each workflow in the project
        """
        _conf = self.config
        _graphs = self.graph_defs

        _jobs = {
            _workflow["name"]: _graphs[_workflow["name"]].to_job()
            for _workflow in _conf["workflows"]
        }

        self.job_defs = _jobs
        # return _jobs

    def _build_schedule_defs(self):
        """
        builds the schedule definitions at which the jobs need to be executed

        :params
            self: Dagmate -> an instance of class Dagmate
        :returns
            _modules: Dict[str,ScheduleDefinition] ->
            a dictionary for loaded modules for each workfllow in the project
        """
        _conf = self.config
        _jobs = self.job_defs

        _schedules = {
            _workflow["name"]: ScheduleDefinition(
                job=_jobs[_workflow["name"]],
                cron_schedule=_workflow["schedule"],
                default_status=DefaultScheduleStatus.RUNNING,
            )
            for _workflow in _conf["workflows"]
        }

        self.schedule_defs = _schedules
        # return _schedules

    def _build_repository_defs(self) -> None:
        """
        builds the repositories and loads them in the globals() namespace
        of the mainframe module from which the grpc server loads

        :params
            self: Dagmate -> an instance of class Dagmate
        :returns
            _repos: Dict[str,RepositoryDefinition]] ->
            a dictionary for loaded repositories for each workflow
        """
        _conf = self.config
        _jobs = self.job_defs
        _schedules = self.schedule_defs

        _repos = {}
        # _g = globals()
        for _workflow in _conf["workflows"]:
            _workflow_name = _workflow["name"]

            @repository(name=_workflow_name)
            def _repo():
                return [_jobs[_workflow_name]] + [_schedules[_workflow_name]]

            _repo.__name__ = _workflow_name
            _repo.__qualname__ = _workflow_name

            # _g[f'__repository__{_workflow_name}'] = _repo
            _repos[_workflow_name] = _repo

            self._mainframe.f_globals[f"__repository__{_workflow_name}"] = _repo
            setattr(self._main, f"__repository__{_workflow_name}", _repo)

        self.repository_defs: Dict[str, RepositoryDefinition] = _repos
        # return _repos
