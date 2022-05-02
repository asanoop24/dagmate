from typing import Union, Dict, List, Tuple
from types import FrameType, ModuleType, TracebackType
from importlib import import_module

from dagster import (
    InputDefinition,
    OutputDefinition,
    get_dagster_logger,
    op,
    Nothing,
    In,
    Out,
    OpDefinition,
    GraphDefinition,
    DependencyDefinition,
    MultiDependencyDefinition,
    job)

_logger = get_dagster_logger()


def create_dynamic_op(
    name: str,
    module: ModuleType,
    in_args: Dict,
    out_args: Dict
    ) -> Tuple[OpDefinition,Dict[str,DependencyDefinition]]:
    
    """
    Args:
        name (str):
            name of the op to be displayed in the graph
        module (ModuleType):
            module/script object imported from the directory

    Returns:
        a tuple with 2 objects
        an OpDefinition object and Dict object with dependency definitions  
    """

    # only create an op for the module if it contains a main function
    if "main" in dir(module):

        # fetching the main function from the module
        _main = module.main
        _name = name
        
        # renaming the main function as the module name
        # this will be displayed as the op name in dagit ui
        _main.__name__ = module.__name__
        
        # preparing the dictionary for ins
        # print([vl for k,vl in in_args[_name].items()])
        ins = {k:In() if len(v)==2 else In(Nothing) for k,v in in_args[_name].items()}
        deps = {k:DependencyDefinition(v[0], v[1]) if len(v)==2 else DependencyDefinition(v[0]) for k,v in in_args[_name].items()}
        out = {v:Out() for v in out_args[_name]}
        
        # wrapping the main function with the op decorator
        # the current process doesn't accept any parameters
        # and is only based on previous ops' execution
        # _op = op(
        #     _name,
        #     ins={
        #         "start": In(Nothing)
        #         }
        #     )(_main)

        _op = op(
            _name,
            ins=ins,
            out=out
            )(_main)

        # _op_def = OpDefinition(name=_op_def, input_defs=[InputDefinition("start",Nothing)], compute_fn=_op_def, output_defs=[OutputDefinition()])
        
        # appending the op to the list of ops
        # _def.append(_op)

        # create dependency definitions fetched from the config file
        _dep = {}
        # _dep = {} if dependencies[_name] is None else {
        #     "start": MultiDependencyDefinition(
        #         [
        #             DependencyDefinition(f"{d}") for d in dependencies[_name]
        #         ]
        #     )
        # }


        _dep = deps

        return _op, _dep
