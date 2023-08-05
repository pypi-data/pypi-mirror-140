import tempfile
from unittest.mock import PropertyMock, patch

from click.testing import CliRunner

from energinetml.cli.model.files import files
from energinetml.core.model import Model
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


@patch("energinetml.cli.model.files.click.echo")
@patch.object(Model, "files", new_callable=PropertyMock)
def test__model_files__should_echo_model_files(model_files_mock, echo_mock):
    """
    :param Mock model_files_mock:
    :param Mock echo_mock:
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

        model_files_mock.return_value = ["file1", "file2"]

        # Act
        result = runner.invoke(cli=files, args=["--path", model.path])

        # Assert
        assert result.exit_code == 0
        assert echo_mock.call_count == 2

        echo_mock.assert_any_call("file1")
        echo_mock.assert_any_call("file2")
