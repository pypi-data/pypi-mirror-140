"""
This is a boilerplate pipeline 'mdp'
generated using Kedro 0.17.6
"""

from kedro.pipeline import Pipeline, node

from .nodes import tratamento, carrega_mdp, resolve_mdp


def create_pipeline(**kwargs) -> Pipeline:
    r""" "
    transformacao create_pipeline
    """
    pipeline_tratamento= Pipeline(
        [
            node(
                tratamento,
                inputs="estacoes",
                outputs="estacoes_limpa",
                name="node_tratamento",
            )
        ]
    )

    pipeline_carrega_mdp = Pipeline(
        [
            node(
                carrega_mdp,
                inputs=["estacoes_limpa", "params:metro_sp_from", "params:metro_sp_to"],
                outputs="MDP",
                name="node_carrega_mdp",
            )
        ]
    )

    pipeline_resolve_mdp = Pipeline(
        [
            node(
                resolve_mdp,
                inputs="MDP",
                outputs="json_resultado",
                name="node_resolve_mdp",
            )
        ]
    )

    return pipeline_tratamento + pipeline_carrega_mdp + pipeline_resolve_mdp
