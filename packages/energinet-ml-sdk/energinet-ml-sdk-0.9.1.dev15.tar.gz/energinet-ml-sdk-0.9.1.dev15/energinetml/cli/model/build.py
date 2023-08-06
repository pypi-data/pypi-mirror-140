#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]
"""
import os

import click

from energinetml.cli.utils import discover_model
from energinetml.core.docker import build_prediction_api_docker_image
from energinetml.core.model import Model


@click.command()
@click.option(
    "--tag",
    "-t",
    required=True,
    help="Name and optionally a tag in the ‘name:tag’ format",
)
@click.option(
    "--model-version",
    "model_version",
    required=True,
    type=str,
    help="Model version (used for logging)",
)
@discover_model()
def build(tag: str, model_version: str, model: Model) -> None:
    """Build a Docker image with a HTTP web API for model prediction.

    Args:
        tag (str): [description]
        model_version (str): [description]
        model (Model): [description]
    """
    with model.temporary_folder(include_trained_model=True) as path:
        build_prediction_api_docker_image(
            path=path,
            trained_model_file_path=os.path.join(path, "outputs", "model.pkl"),
            model_version=model_version,
            tag=tag,
        )
