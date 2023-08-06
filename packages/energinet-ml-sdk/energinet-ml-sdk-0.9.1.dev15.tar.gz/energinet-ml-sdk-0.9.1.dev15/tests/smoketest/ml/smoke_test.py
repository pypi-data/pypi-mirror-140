"""[summary]
"""
import binascii
import json
import os
import shutil
import subprocess
import sys
import typing
from datetime import datetime

import pytest
from azureml.core import ComputeTarget, Experiment, Model, Workspace
from azureml.core.run import Run

from energinetml import TrainedModel
from energinetml.settings import DEFAULT_LOG_FILENAME, PACKAGE_NAME, PACKAGE_REQUIREMENT

# from energinetml.settings import DEFAULT_LOG_ENCODING


# -- Constants ---------------------------------------------------------------


CLUSTER_NAME = f"SmokeTest-{binascii.b2a_hex(os.urandom(2)).decode('utf8')}"

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
MODEL_SCRIPT_FILE_PATH = os.path.join(CURRENT_DIR, "model.py")


# -- Common ------------------------------------------------------------------


@pytest.fixture
def workspace(subscription_id, resource_group, workspace_name):
    """[summary]"""
    yield Workspace.get(
        subscription_id=subscription_id,
        resource_group=resource_group,
        name=workspace_name,
    )


@pytest.fixture
def project_folder_path(project_name):
    """
    The project's root path, ie. the folder in which project.json is.

    :param str project_name:
    """
    return os.path.join(CURRENT_DIR, project_name)


@pytest.fixture
def model_folder_path(model_name, project_folder_path):
    """
    The project's root path, ie. the folder in which project.json is.

    :param str model_name:
    :param str project_folder_path:
    """
    return os.path.join(project_folder_path, model_name)


@pytest.fixture
def requirements_file_path(project_folder_path):
    """
    :param str project_folder_path:
    """
    return os.path.join(project_folder_path, "requirements.txt")


def _exec(command):
    """
    :param typing.List[str] command:
    :rtype: int
    """
    return subprocess.check_call(command, stdout=sys.stdout, stderr=subprocess.STDOUT)


def _exec_get_output(command):
    """
    :param typing.List[str] command:
    :rtype: str
    """
    return subprocess.check_output(command).decode("utf-8")


def _get_latest_run(workspace, model_name):
    """
    Returns the most recent Run in this experiment, or None.

    :param Workspace workspace:
    :param str model_name:
    :rtype: Run
    """
    experiment = Experiment(workspace, model_name)
    runs = sorted(
        experiment.get_runs(),
        key=lambda run: _parse_azureml_datetime(run.get_details()["startTimeUtc"]),
        reverse=True,
    )
    return runs[0] if runs else None


def _parse_azureml_datetime(s_time_utc: str) -> datetime:
    """
    :param str s_time_utc:
    :rtype: datetime
    """
    return datetime.strptime(s_time_utc, "%Y-%m-%dT%H:%M:%S.%fZ")


def _check_if_logs_exists(
    run: Run, sys_outs: typing.List[str] = ["stdout", "stderr"]
) -> None:
    """The function checks for captured logfiles.
    TODO:  ["stdout", "stderr"] depends on the naming in energinetml.cli.model.train().
    Maybe we can find a better solution?

    Args:
        run ([azureml.core.run.Run]): run returned from _get_latest_run().
        sys_outs (typing.List[str, str], optional):
        List of names for the captured log files. Defaults to ["stdout", "stderr"].

    """

    file_prefix, ext = DEFAULT_LOG_FILENAME.split(".")
    log_files = [
        filename for filename in run.get_file_names() if filename.endswith(ext)
    ]

    for out in sys_outs:
        filename = f"{file_prefix}_{out}.{ext}"
        assert filename in log_files, f"{filename} is missing."


# -- Tests -------------------------------------------------------------------


@pytest.mark.order(0)
def test__energinetml__clean_up(project_folder_path):
    """
    Cleans up after previous test runs.

    :param str project_folder_path:
    """
    if os.path.exists(project_folder_path):
        shutil.rmtree(project_folder_path)


@pytest.mark.order(1)
def test__energinetml__project_init(
    subscription_id,
    subscription_name,
    resource_group,
    workspace_name,
    project_name,
    project_folder_path,
):
    """
    Init a new project on the filesystem.
    AzureML Workspace must exist already.

    :param str subscription_id:
    :param str subscription_name:
    :param str resource_group:
    :param str workspace_name:
    :param str project_name:
    :param str project_folder_path:
    """

    # -- Act -----------------------------------------------------------------

    result = _exec(
        [
            "energinetml",
            "project",
            "init",
            "--path",
            project_folder_path,
            "--name",
            project_name,
            "--subscription",
            subscription_name,
            "--resource-group",
            resource_group,
            "--workspace",
            workspace_name,
        ]
    )

    # -- Assert --------------------------------------------------------------

    assert result == 0
    assert os.path.isfile(os.path.join(project_folder_path, "project.json"))
    assert os.path.isfile(os.path.join(project_folder_path, "requirements.txt"))

    with open(os.path.join(project_folder_path, "project.json")) as handle:
        config = json.load(handle)
        assert config["name"] == project_name
        assert config["resource_group"] == resource_group
        assert config["subscription_id"] == subscription_id
        assert config["workspace_name"] == workspace_name

    with open(os.path.join(project_folder_path, "requirements.txt")) as handle:
        assert str(PACKAGE_REQUIREMENT) in handle.read()


@pytest.mark.order(2)
@pytest.mark.depends(on=["test__energinetml__project_init"])
def test__energinetml__model_init(model_name, project_folder_path, model_folder_path):
    """
    Init a new model on the filesystem.

    :param str model_name:
    :param str project_folder_path:
    :param str model_folder_path:
    """

    # -- Act -----------------------------------------------------------------

    result = _exec(
        [
            "energinetml",
            "model",
            "init",
            "--path",
            project_folder_path,
            "--name",
            model_name,
            "--cluster",
            "no",
        ]
    )

    # -- Assert --------------------------------------------------------------

    assert result == 0
    assert os.path.isfile(os.path.join(model_folder_path, "__init__.py"))
    assert os.path.isfile(os.path.join(model_folder_path, "model.py"))
    assert os.path.isfile(os.path.join(model_folder_path, "model.json"))

    with open(os.path.join(model_folder_path, "model.json")) as handle:
        config = json.load(handle)
        assert config["name"] == model_name
        assert config["experiment"] == model_name
        assert config["compute_target"] is None
        assert config["vm_size"] is None
        assert config["datasets"] == []
        assert config["features"] == []
        assert config["parameters"] == {}


@pytest.mark.order(3)
@pytest.mark.depends(on=["test__energinetml__model_init"])
def test__energinetml__cluster_create(workspace, model_folder_path):
    """
    Create a new compute cluster.

    :param Workspace workspace:
    :param str model_folder_path:
    """

    # -- Act -----------------------------------------------------------------

    result = _exec(
        [
            "energinetml",
            "cluster",
            "create",
            "--path",
            model_folder_path,
            "--cluster-name",
            CLUSTER_NAME,
            "--min-nodes",
            "0",
            "--max-nodes",
            "1",
            "--default",
            "--cpu",
        ]
    )

    # -- Assert --------------------------------------------------------------

    assert result == 0

    compute_target = ComputeTarget(workspace, CLUSTER_NAME)

    assert compute_target.name == CLUSTER_NAME

    with open(os.path.join(model_folder_path, "model.json")) as handle:
        config = json.load(handle)
        assert config["compute_target"] == CLUSTER_NAME


@pytest.mark.order(4)
@pytest.mark.depends(on=["test__energinetml__cluster_create"])
def test__energinetml__model_train(
    workspace, model_name, model_folder_path, requirements_file_path, sdk_version
):
    """
    Executes a training locally.

    :param Workspace workspace:
    :param str model_name:
    :param str model_folder_path:
    :param str requirements_file_path:
    :param str sdk_version:
    """

    # -- Arrange -------------------------------------------------------------

    with open(requirements_file_path) as handle:
        requirements = handle.readlines()

    # Add model requirements
    requirements.append("scikit-learn\n")
    requirements = "".join(requirements)

    os.unlink(requirements_file_path)

    # Install PIP requirements
    with open(requirements_file_path, "w") as handle:
        handle.write(requirements)

    # Overwrite SDK version from requirements.txt
    _exec(["pip", "install", "-r", requirements_file_path, "--pre"])

    # Copy model script
    shutil.copyfile(
        src=MODEL_SCRIPT_FILE_PATH, dst=os.path.join(model_folder_path, "model.py")
    )

    # Add dataset to model.json
    with open(os.path.join(model_folder_path, "model.json")) as handle:
        doc = json.load(handle)
        doc["datasets"].append("smoketest-dataset")
        doc["datasets_local"].append("smoketest-dataset-local")
        doc["datasets_cloud"].append("smoketest-dataset-cloud")
    with open(os.path.join(model_folder_path, "model.json"), "w") as handle:
        json.dump(doc, handle)

    # Latest run number
    # Runs start from 1, so set it to 0 if no previous runs
    latest_run = _get_latest_run(workspace, model_name)
    if latest_run:
        latest_run_time = _parse_azureml_datetime(
            latest_run.get_details()["startTimeUtc"]
        )  # noqa: E501
    else:
        latest_run_time = None

    # -- Act -----------------------------------------------------------------

    result = _exec(
        [
            "energinetml",
            "model",
            "train",
            "--path",
            model_folder_path,
            "--seed",
            "12345",
            "--force-download",
        ]
    )

    # -- Assert --------------------------------------------------------------

    assert result == 0

    run = _get_latest_run(workspace, model_name)

    if latest_run_time:
        run_time = _parse_azureml_datetime(run.get_details()["startTimeUtc"])
        assert run_time > latest_run_time

    assert run.status == "Completed"
    assert run.tags["seed"] == "12345"
    assert run.tags["datasets"] == "smoketest-dataset, smoketest-dataset-local"
    assert run.tags[PACKAGE_NAME] == str(sdk_version)

    # Will raise exception on failure:
    # TODO Verify trained model?
    TrainedModel.load(os.path.join(model_folder_path, "outputs", "model.pkl"))
    _check_if_logs_exists(run=run, sys_outs=["stdout", "stderr"])


@pytest.mark.order(5)
@pytest.mark.depends(on=["test__energinetml__model_train"])
def test__energinetml__model_submit(
    workspace, model_name, model_folder_path, sdk_version
):
    """
    Submits the model to training in the cloud.

    :param Workspace workspace:
    :param str model_name:
    :param str model_folder_path:
    """

    # -- Clean up ------------------------------------------------------------

    if os.path.exists(os.path.join(model_folder_path, "outputs")):
        shutil.rmtree(os.path.join(model_folder_path, "outputs"))
    if os.path.exists(os.path.join(model_folder_path, "logs")):
        shutil.rmtree(os.path.join(model_folder_path, "logs"))
    if os.path.exists(os.path.join(model_folder_path, "azureml-logs")):
        shutil.rmtree(os.path.join(model_folder_path, "azureml-logs"))

    # -- Arrange -------------------------------------------------------------

    latest_run = _get_latest_run(workspace, model_name)
    latest_run_time = _parse_azureml_datetime(latest_run.get_details()["startTimeUtc"])

    # -- Act -----------------------------------------------------------------

    result = _exec(
        [
            "energinetml",
            "model",
            "submit",
            "--path",
            model_folder_path,
            "--seed",
            "67890",
            "--wait",
            "--download",
        ]
    )

    # -- Assert --------------------------------------------------------------

    assert result == 0

    run = _get_latest_run(workspace, model_name)
    run_time = _parse_azureml_datetime(run.get_details()["startTimeUtc"])
    assert run_time > latest_run_time
    assert run.status == "Completed"
    assert run.tags["seed"] == "67890"
    assert run.tags["datasets"] == "smoketest-dataset, smoketest-dataset-cloud"
    assert run.tags[PACKAGE_NAME] == str(sdk_version)

    # Will raise exception on failure:
    # TODO Verify trained model?
    TrainedModel.load(os.path.join(model_folder_path, "outputs", "model.pkl"))
    _check_if_logs_exists(run=run, sys_outs=["stdout", "stderr"])


@pytest.mark.order(6)
@pytest.mark.depends(on=["test__energinetml__model_submit"])
def test__energinetml__model_predict(
    model_folder_path, prediction_input, prediction_output
):
    """
    Predict locally using the model trained in the cloud.
    The model was downloaded to local filesystem after training in cloud.

    :param str model_folder_path:
    :param typing.Any prediction_input:
    :param typing.Any prediction_output:
    """

    # -- Act -----------------------------------------------------------------

    output = _exec_get_output(
        [
            "energinetml",
            "model",
            "predict",
            "--path",
            model_folder_path,
            "--json",
            json.dumps(prediction_input),
        ]
    )

    # -- Assert --------------------------------------------------------------

    result_json = json.loads(output)
    assert result_json["predictions"] == prediction_output


@pytest.mark.order(7)
@pytest.mark.depends(on=["test__energinetml__model_predict"])
def test__energinetml__model_release(
    workspace, project_name, model_name, model_folder_path, sdk_version
):
    """
    Releases the model trained in the cloud.

    :param Workspace workspace:
    :param str project_name:
    :param str model_name:
    :param str model_folder_path:
    """

    # -- Arrange -------------------------------------------------------------

    latest_run = _get_latest_run(workspace, model_name)

    # -- Act -----------------------------------------------------------------

    result = _exec(
        [
            "energinetml",
            "model",
            "release",
            "--path",
            model_folder_path,
            "--run-id",
            latest_run.id,
        ]
    )

    # -- Assert --------------------------------------------------------------

    assert result == 0

    model = Model(workspace, name=project_name)
    assert model.tags["seed"] == "67890"
    assert model.tags[PACKAGE_NAME] == str(sdk_version)
