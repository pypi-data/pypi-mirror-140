import tempfile
from unittest.mock import ANY, patch

from click.testing import CliRunner

from energinetml.cli.model.build import build
from energinetml.core.model import Model, TrainedModel
from energinetml.core.project import MachineLearningProject

# Project
PROJECT_NAME = "PROJECTNAME"
SUBSCRIPTION_ID = "SUBSCRIPTION-ID"
RESOURCE_GROUP = "RESOURCE-GROUP"
WORKSPACE_NAME = "WORKSPACE-NAME"
VNET = "VNET"
SUBNET = "SUBNET"


# Model
MODEL_NAME = "MODELNAME"
EXPERIMENT = "EXPERIMENT"
COMPUTE_TARGET = "COMPUTE-TARGET"
VM_SIZE = "VM-SIZE"
DATASETS = ["iris", "hades:2"]
FEATURES = ["feature1", "feature2"]
PARAMETERS = {"param1": "value1", "param2": "value2"}


# -- create() Tests ----------------------------------------------------------


@patch("energinetml.cli.model.build.build_prediction_api_docker_image")
def test__build_model__should__build_docker_image(
    build_prediction_api_docker_image_mock,
):
    """
    :param Mock build_prediction_api_docker_image_mock:
    """
    runner = CliRunner()

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

        model = Model.create(
            path=project.default_model_path(MODEL_NAME),
            name=MODEL_NAME,
            experiment=EXPERIMENT,
            compute_target=COMPUTE_TARGET,
            vm_size=VM_SIZE,
            datasets=DATASETS,
            features=FEATURES,
            parameters=PARAMETERS,
        )

        TrainedModel(model="123").dump(model.trained_model_path)  # Just not None

        # copyfile()

        # Act
        result = runner.invoke(
            cli=build,
            args=[
                "--path",
                model.path,
                "--tag",
                "docker:tag",
                "--model-version",
                "123",
            ],
        )

        # Assert
        assert result.exit_code == 0

        build_prediction_api_docker_image_mock.assert_called_once_with(
            path=ANY,  # Temporary directory
            trained_model_file_path=ANY,
            model_version="123",
            tag="docker:tag",
        )
