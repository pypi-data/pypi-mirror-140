#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]
"""
import click

from energinetml.cli.utils import discover_model, discover_trained_model
from energinetml.core.http import run_predict_api
from energinetml.core.model import Model, TrainedModel


@click.command()
@discover_model()
@discover_trained_model()
@click.option(
    "--host",
    default="127.0.0.1",
    type=str,
    help="Host to serve on (default: 127.0.0.1)",
)
@click.option("--port", default=8080, type=int, help="Port to serve on (default: 8080)")
@click.option(
    "--model-version",
    "model_version",
    required=False,
    type=str,
    default="Unspecified",
    help="Model version (used for logging)",
)
def serve(
    host: str,
    port: int,
    model: Model,
    trained_model: TrainedModel,
    model_version: str = None,
) -> None:
    """Serve a HTTP web API for model prediction.

    Args:
        host (str): [description]
        port (int): [description]
        model (Model): [description]
        trained_model (TrainedModel): [description]
        model_version (str, optional): [description]. Defaults to None.
    """
    run_predict_api(
        model=model,
        trained_model=trained_model,
        model_version=model_version,
        host=host,
        port=port,
    )
