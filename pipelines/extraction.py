from dagster import (
    get_dagster_logger,
    op,
    Nothing,
    In,
    Out,
    GraphDefinition,
    DependencyDefinition,
    MultiDependencyDefinition,
    job,
)

_logger = get_dagster_logger()


@op(out={"out_1": Out(), "out_2": Out()})
def extract_1():
    _logger.info("extraction 1 completed!")
    return "A", "B"


@op
def extract_1_1():
    _logger.info("extraction 1_1 completed!")
    return "A", "B"


@op(ins={"in_1": In(Nothing), "in_2": In()}, out={"out_1": Out(), "out_2": Out()})
def extract_2(in_2):
    _logger.info(f"Only Input is {in_2}")
    _logger.info("extraction 2 completed!")
    return "C", "D"


@op(ins={"in_1": In(), "in_2": In()}, out={"out_1": Out()})
def extract_3(in_1, in_2):
    _logger.info(f"Input 1 is {in_1}")
    _logger.info(f"Input 2 is {in_2}")
    _logger.info("extraction 3 completed!")
    return "E"


print(extract_2)
print(dir(extract_2))

extraction_graph = GraphDefinition(
    name="extraction",
    node_defs=[extract_1, extract_1_1, extract_2, extract_3],
    dependencies={
        "extract_1": {},
        "extract_2": {
            "in_1": DependencyDefinition("extract_1_1"),
            "in_2": DependencyDefinition("extract_1", "out_2"),
        },
        "extract_3": {
            "in_1": DependencyDefinition("extract_2", "out_1"),
            "in_2": DependencyDefinition("extract_2", "out_2"),
        },
    },
)

extraction_job = extraction_graph.to_job()
