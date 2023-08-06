"""Project pipelines."""
from typing import Dict

from kedro.pipeline import Pipeline

from metro_sp_mdp.pipelines import mdp


def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from a pipeline name to a ``Pipeline`` object.
    """

    pipeline_mdp = mdp.create_pipeline()

    return {
        "pipe_mdp" : pipeline_mdp,
        "__default__": pipeline_mdp
        }
