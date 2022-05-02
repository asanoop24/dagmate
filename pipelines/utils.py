from typing import Union, Dict, List, Tuple
from types import FrameType, ModuleType, TracebackType
from importlib import import_module

from dagster import (
    get_dagster_logger,
    op,
    Nothing,
    In,
    Out,
    OpDefinition,
    DependencyDefinition,
    MultiDependencyDefinition)

_logger = get_dagster_logger()


def create_dynamic_op(
    name: str,
    module: ModuleType,
    inputs: Dict,
    outputs: Dict
    ) -> Tuple[OpDefinition,Dict[str,DependencyDefinition]]:
    
    """
    Args:
        name (str):
            name of the op to be displayed in the graph
        module (ModuleType):
            module/script object imported from the directory
        inputs (Dict):
            dictionary of input dependencies as defined in config file
        outputs (Dict):
            dictionary of output dependencies as defined in config file

    Returns:
        a tuple with 2 objects
        an OpDefinition object and Dict object with dependency definitions  
    """

    # only create an op for the module if it contains a step_fn function
    if "step_fn" in dir(module):

        # fetching the step_fn function from the module
        _step_fn = module.step_fn
        _name = name
        
        # renaming the main function as the module name
        # this will be displayed as the op name in dagit ui
        _step_fn.__name__ = module.__name__
        
        # preparing the dictionary for ins
        _ins = {k:In() if len(v)==2 else In(Nothing) for k,v in inputs[_name].items()}
        _dep = {k:DependencyDefinition(v[0], v[1]) if len(v)==2 else DependencyDefinition(v[0]) for k,v in inputs[_name].items()}
        _out = {v:Out() for v in outputs[_name]}
        
        # wrapping the main function with the op decorator
        # the current process doesn't accept any parameters
        # and is only based on previous ops' execution
        _op = op(_name, ins=_ins, out=_out)(_step_fn)

        return _op, _dep
