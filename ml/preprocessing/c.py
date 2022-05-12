# import pandas as pd

from dagster import get_dagster_logger

_logger = get_dagster_logger()


def step_fn(x1, x2):

    # df = pd.DataFrame(data=[[x1, x2], [2 * x1, 2 * x2]], columns=["AX", "BY"])
    # _logger.info(df)
    _logger.info("I am C! Whats up")
    return 10, 20


if __name__ == "__main__":
    step_fn()
