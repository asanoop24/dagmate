from dagster import (
    DefaultScheduleStatus,
    GraphDefinition,
    NodeInvocation,
    ScheduleDefinition,
    get_dagster_logger,
    make_email_on_run_failure_sensor,
    repository,
)

_logger = get_dagster_logger()

import os
from importlib import import_module

_EMAIL_FROM = "XXXX@gmail.com"
_EMAIL_PASSWORD = "XXXXXX"
_EMAIL_TO = "XXXX@gmail.com"
_SMTP_HOST = "smtp.office365.com"
_SMTP_PORT = 587
_SMTP_TYPE = "STARTTLS"  # or SSL

_PROJECT_NAME = "apml"
_utils = import_module("utils", f"{_PROJECT_NAME}")
_op_builder = _utils.build_op_from_module


_pipelines = [f for f in os.listdir(".") if os.path.isdir(f) and "__conf__.py" in os.listdir(f)]

_jobs = []
_schedules = []
_sensors = []
for _pipeline in _pipelines:

    # reading the configuration file for the pipeline and dependencies
    _conf = import_module(f"{_PROJECT_NAME}.{_pipeline}.__conf__")
    _modules = _conf.steps
    _inputs = _conf.inputs
    _outputs = _conf.outputs

    _ops = []
    _deps = {}
    for _name in _modules:
        if _name == "__conf__":
            continue

        # importing the module that needs to be converted to the workflow step (op)
        _module = import_module(f"{_PROJECT_NAME}.{_pipeline}.{_name}")

        # assigning a unique name to the op to prevent naming conflicts with other pipelines
        _uname = f"{_pipeline}__{_name}"

        # creating the op using the parameters defined
        _op, _dep = _op_builder(_name, _pipeline, _module, _inputs, _outputs)

        # appending op to the node_defs list that will be used during the job creation
        _ops.append(_op)

        # creating the dependency dictionary that will be used during the job creation
        _deps[NodeInvocation(_uname, _name)] = _dep

    # creating the job for the pipeline using the ops and dependencies generated above
    _job = GraphDefinition(name=_pipeline, node_defs=_ops, dependencies=_deps).to_job()
    _schedule = ScheduleDefinition(
        job=_job, cron_schedule="*/1 * * * *", default_status=DefaultScheduleStatus.RUNNING
    )
    _schedules.append(_schedule)

_sensor = make_email_on_run_failure_sensor(
    email_from=_EMAIL_FROM,
    email_password=_EMAIL_PASSWORD,
    email_to=_EMAIL_TO,
    smtp_host=_SMTP_HOST,
    smtp_port=_SMTP_PORT,
    smtp_type=_SMTP_TYPE,
    job_selection=_jobs,
)
_sensors.append(_sensor)


@repository(name=_PROJECT_NAME)
def repo():
    return _jobs + _schedules + _sensors
