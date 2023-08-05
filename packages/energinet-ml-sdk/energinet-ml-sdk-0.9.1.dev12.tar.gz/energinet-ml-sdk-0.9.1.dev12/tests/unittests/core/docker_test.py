import os
import subprocess
import sys
from unittest.mock import patch

import pytest

from energinetml.core.docker import build_prediction_api_docker_image
from energinetml.settings import DOCKERFILE_PATH_ML_MODEL, PACKAGE_VERSION

TRAINED_MODEL_FILENAME = "model.pkl"


@patch("energinetml.core.docker.subprocess.check_call")
def test__build_prediction_api_docker_image__happy_path(check_call_mock):
    """
    :param Mock check_call_mock:
    """
    path = os.path.join("some", "arbitrary", "path")
    tag = "my-model:v1"
    trained_model_file_path = os.path.join(path, "output", TRAINED_MODEL_FILENAME)
    model_version = "123"

    build_prediction_api_docker_image(
        path=path,
        tag=tag,
        trained_model_file_path=trained_model_file_path,
        model_version=model_version,
    )

    # Assert

    expected_command = [
        "docker",
        "build",
        "--tag",
        tag,
        "--file",
        DOCKERFILE_PATH_ML_MODEL,
        "--build-arg",
        "TRAINED_MODEL_PATH=%s" % os.path.join("output", TRAINED_MODEL_FILENAME),
        "--build-arg",
        "MODEL_VERSION=%s" % model_version,
        "--build-arg",
        "PACKAGE_VERSION=%s" % PACKAGE_VERSION,
        path,
    ]

    check_call_mock.assert_called_once_with(
        expected_command, stdout=sys.stdout, stderr=subprocess.STDOUT, shell=False
    )


def test__build_prediction_api_docker_image__trained_model_path_is_outside_path__should_raise_value_error():  # noqa: E501
    path = os.path.join("some", "arbitrary", "path")
    trained_model_file_path = os.path.join(
        "another", "arbitrary", "path", TRAINED_MODEL_FILENAME
    )

    with pytest.raises(ValueError):
        build_prediction_api_docker_image(
            path=path,
            tag="asd",
            trained_model_file_path=trained_model_file_path,
            model_version="123",
        )
