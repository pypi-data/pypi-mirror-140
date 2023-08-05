#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]
"""

import os
import subprocess
import sys
from typing import Dict

from energinetml.core.project import WebAppProject
from energinetml.settings import DOCKERFILE_PATH_ML_MODEL, PACKAGE_VERSION


def build_prediction_api_docker_image(
    path: str, tag: str, trained_model_file_path: str, model_version: str
) -> None:
    """TODO: Add package version when installing energinet-ml-sdk

    Args:
        path (str): [description]
        tag (str): [description]
        trained_model_file_path (str): [description]
        model_version (str): [description]

    Raises:
        ValueError: [description]
    """
    trained_model_file_real_path = os.path.realpath(trained_model_file_path)
    trained_model_file_relative_path = os.path.relpath(trained_model_file_path, path)
    model_real_path = os.path.realpath(path)

    if not trained_model_file_real_path.startswith(model_real_path):
        raise ValueError(
            (
                "Trained model file must be located within the model folder. "
                f"You are trying to add file '{trained_model_file_path}' which is "
                f"not located within the model folder ({path}). "
                "This is not supported by Docker."
            )
        )

    build_docker_image(
        path=path,
        tag=tag,
        dockerfile_path=DOCKERFILE_PATH_ML_MODEL,
        build_args={
            "TRAINED_MODEL_PATH": trained_model_file_relative_path,
            "MODEL_VERSION": model_version,
        },
    )


def build_webapp_docker_image(project: WebAppProject, tag: str) -> None:
    """TODO: Add package version when installing energinet-ml-sdk

    Args:
        project (project.WebAppProject): [description]
        tag (str): [description]
    """
    build_docker_image(
        path=project.path, tag=tag, dockerfile_path=project.dockerfile_path
    )


def build_docker_image(
    path: str,
    tag: str,
    params: Dict[str, str] = None,
    build_args: Dict[str, str] = None,
    dockerfile_path: str = None,
):
    """Build a Docker image.

    Args:
        path (str): [description]
        tag (str): [description]
        params (Dict[str, str], optional): [description]. Defaults to None.
        build_args (Dict[str, str], optional): [description]. Defaults to None.
        dockerfile_path (str, optional): [description]. Defaults to None.
    """
    if params is None:
        params = {}
    if build_args is None:
        build_args = {}

    if dockerfile_path:
        params["--file"] = dockerfile_path

    build_args["PACKAGE_VERSION"] = str(PACKAGE_VERSION)

    # Render 'docker build' command
    command = ["docker", "build"]
    command.extend(("--tag", tag))
    for k, v in params.items():
        command.extend((k, v))
    for k, v in build_args.items():
        command.extend(("--build-arg", f"{k}={v}"))
    command.append(path)

    # Run 'docker build' command in subprocess
    subprocess.check_call(
        command, stdout=sys.stdout, stderr=subprocess.STDOUT, shell=False
    )
