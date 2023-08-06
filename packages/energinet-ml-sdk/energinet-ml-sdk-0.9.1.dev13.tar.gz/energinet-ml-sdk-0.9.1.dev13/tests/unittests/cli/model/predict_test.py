import os
import tempfile
from pathlib import Path
from unittest.mock import ANY, Mock, patch

import pydantic
import pytest
from click.testing import CliRunner

from energinetml.cli.model.predict import predict
from energinetml.core.model import Model, TrainedModel
from energinetml.core.project import MachineLearningProject

# Project
PROJECT_NAME = "NAME"
SUBSCRIPTION_ID = "SUBSCRIPTION-ID"
RESOURCE_GROUP = "RESOURCE-GROUP"
WORKSPACE_NAME = "WORKSPACE-NAME"
VNET = "VNET"
SUBNET = "SUBNET"


# Model
MODEL_NAME = "NAME"
EXPERIMENT = "EXPERIMENT"
COMPUTE_TARGET = "COMPUTE-TARGET"
VM_SIZE = "VM-SIZE"
DATASETS = ["iris", "hades:2"]
FEATURES = ["feature1", "feature2"]
PARAMETERS = {"param1": "value1", "param2": "value2"}

# This satisfies SonarCloud
JSON_FILE_NAME = "something.json"
VALID_JSON = '{"valid": "json"}'


@pytest.fixture
def model_path():
    with tempfile.TemporaryDirectory() as path:
        project = MachineLearningProject.create(
            path=path,
            name=PROJECT_NAME,
            subscription_id=SUBSCRIPTION_ID,
            resource_group=RESOURCE_GROUP,
            workspace_name=WORKSPACE_NAME,
            vnet_name=VNET,
            subnet_name=SUBNET,
        )

        model_path = project.default_model_path(MODEL_NAME)

        model = Model.create(
            path=model_path,
            name=MODEL_NAME,
            experiment=EXPERIMENT,
            compute_target=COMPUTE_TARGET,
            vm_size=VM_SIZE,
            datasets=DATASETS,
            features=FEATURES,
            parameters=PARAMETERS,
        )

        TrainedModel(model="123", params={"asd": 123}, features=FEATURES).dump(
            model.trained_model_path
        )

        yield model_path


# -- Tests -------------------------------------------------------------------


def test__model_predict__no_json_provided__should_abort(model_path):
    """
    :param str model_path:
    """
    runner = CliRunner()

    # Act
    result = runner.invoke(cli=predict, args=["--path", model_path])

    # Assert
    assert result.exit_code == 1
    assert result.output.startswith(
        "You must provide me with either the -j/--json "
        "or the -f/--json-file parameter"
    )


def test__model_predict__both_json_file_and_input_string_provided__should_abort(
    model_path,
):  # noqa: E501
    """
    :param str model_path:
    """
    runner = CliRunner()

    json_file_path = os.path.join(model_path, JSON_FILE_NAME)
    Path(json_file_path).touch()

    # Act
    result = runner.invoke(
        cli=predict,
        args=[
            "--path",
            model_path,
            "--json",
            '{"foo": "bar"}',
            "--json-file",
            json_file_path,
        ],
    )

    # Assert
    assert result.exit_code == 1
    assert result.output.startswith(
        "Do not provide me with both the -j/--json and the "
        "-f/--json-file parameter, I only need one."
    )


def test__model_predict__invalid_json_provided__should_abort(model_path):
    """
    :param str model_path:
    """
    runner = CliRunner()

    json_file_path = os.path.join(model_path, JSON_FILE_NAME)
    Path(json_file_path).write_text("this is invalid JSON")

    # Act
    result = runner.invoke(
        cli=predict, args=["--path", model_path, "--json-file", json_file_path]
    )

    # Assert
    assert result.exit_code == 1
    assert result.output.startswith("Failed to parse input json")


@patch("energinetml.cli.model.predict.pydantic.parse_obj_as")
def test__model_predict__pydantic_fails_to_deserialize_json_to_model__should_abort(
    parse_obj_as_mock, model_path
):
    """
    :param Mock parse_obj_as_mock:
    :param str model_path:
    """
    runner = CliRunner()

    test_pydantic_model = pydantic.create_model(
        __model_name="PydanticMockModel", something=str
    )

    parse_obj_as_mock.side_effect = pydantic.error_wrappers.ValidationError(
        [], test_pydantic_model
    )

    json_file_path = os.path.join(model_path, JSON_FILE_NAME)
    Path(json_file_path).write_text(VALID_JSON)

    # Act
    result = runner.invoke(
        cli=predict, args=["--path", model_path, "--json-file", json_file_path]
    )

    # Assert
    assert result.exit_code == 1
    assert result.output.startswith(
        "Invalid input JSON provided. Error description follows"
    )


@patch("energinetml.cli.model.predict.PredictionController")
@patch("energinetml.cli.model.predict.pydantic.parse_obj_as")
def test__model_predict__model_not_implemented__should_abort(
    parse_obj_as_mock, prediction_controller_mock, model_path
):
    """
    :param Mock parse_obj_as_mock:
    :param Mock prediction_controller_mock:
    :param str model_path:
    """
    runner = CliRunner()

    predict_model = Mock()
    controller = Mock()
    controller.predict.side_effect = NotImplementedError

    prediction_controller_mock.return_value = controller
    parse_obj_as_mock.return_value = predict_model

    json_file_path = os.path.join(model_path, JSON_FILE_NAME)
    Path(json_file_path).write_text(VALID_JSON)

    # Act
    result = runner.invoke(
        cli=predict, args=["--path", model_path, "--json-file", json_file_path]
    )

    # Assert
    assert result.exit_code == 1
    assert (
        "The predict() method of your model raised a NotImplementedError "
        "which indicates that you have not yet implemented it."
    ) in result.output


@patch("energinetml.cli.model.predict.PredictionController")
@patch("energinetml.cli.model.predict.pydantic.parse_obj_as")
@patch("energinetml.cli.model.predict.json.dumps")
@patch("energinetml.cli.model.predict.click.echo")
def test__model_predict__everything_ok__should_dump_prediction(
    echo_mock, dumps_mock, parse_obj_as_mock, prediction_controller_mock, model_path
):
    """
    :param Mock dumps_mock:
    :param Mock parse_obj_as_mock:
    :param Mock prediction_controller_mock:
    :param str model_path:
    """
    runner = CliRunner()

    prediction_dict = {"my": "json"}
    dumped_json = '{"my": "json"}'

    predict_model = Mock()
    controller = Mock()
    prediction = Mock()
    prediction.dict.return_value = prediction_dict
    controller.predict.return_value = prediction

    prediction_controller_mock.return_value = controller
    parse_obj_as_mock.return_value = predict_model
    dumps_mock.return_value = dumped_json

    json_file_path = os.path.join(model_path, JSON_FILE_NAME)
    Path(json_file_path).write_text(VALID_JSON)

    # Act
    result = runner.invoke(
        cli=predict, args=["--path", model_path, "--json-file", json_file_path]
    )

    # Assert
    assert result.exit_code == 0

    dumps_mock.assert_called_once_with(prediction_dict, indent=ANY)
    echo_mock.assert_called_once_with(dumped_json)
