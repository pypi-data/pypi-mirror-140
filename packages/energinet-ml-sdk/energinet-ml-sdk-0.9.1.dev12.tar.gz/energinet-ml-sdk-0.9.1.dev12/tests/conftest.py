import tempfile

import pytest

from energinetml.core.model import Model
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

        yield model.path


@pytest.fixture
def model():
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

        yield Model.create(
            path=project.default_model_path(MODEL_NAME),
            name=MODEL_NAME,
            experiment=EXPERIMENT,
            compute_target=COMPUTE_TARGET,
            vm_size=VM_SIZE,
            datasets=DATASETS,
            features=FEATURES,
            parameters=PARAMETERS,
        )


# -- Smoketest command-line options ------------------------------------------


def pytest_addoption(parser):
    """
    Adds command-line options to "pytest" command which will
    become available when running tests. Used for smoke testing.
    """
    parser.addoption("--path", action="store", default=None)
    parser.addoption("--subscription-id", action="store", default=None)
    parser.addoption("--subscription-name", action="store", default=None)
    parser.addoption("--resource-group", action="store", default=None)
    parser.addoption("--service-connection", action="store", default=None)
    parser.addoption("--workspace-name", action="store", default=None)
    parser.addoption("--project-name", action="store", default=None)
    parser.addoption("--model-name", action="store", default=None)
    parser.addoption("--deployment-base-url", action="store", default=None)
    parser.addoption("--sdk-version", action="store", default=None)


@pytest.fixture
def path(pytestconfig):
    """
    Used by ML smoketests.
    """
    return pytestconfig.getoption("--path")


@pytest.fixture
def subscription_id(pytestconfig):
    """
    Used by ML smoketests.
    """
    return pytestconfig.getoption("--subscription-id")


@pytest.fixture
def subscription_name(pytestconfig):
    """
    Used by ML smoketests.
    """
    return pytestconfig.getoption("--subscription-name")


@pytest.fixture
def resource_group(pytestconfig):
    """
    Used by ML AND Web-App smoketests.
    """
    return pytestconfig.getoption("--resource-group")


@pytest.fixture
def service_connection(pytestconfig):
    """
    Used by Web-App smoketests.
    """
    return pytestconfig.getoption("--service-connection")


@pytest.fixture
def workspace_name(pytestconfig):
    """
    Used by ML smoketests.
    """
    return pytestconfig.getoption("--workspace-name")


@pytest.fixture
def project_name(pytestconfig):
    """
    Used by ML AND Web-App smoketests.
    """
    return pytestconfig.getoption("--project-name")


@pytest.fixture
def model_name(pytestconfig):
    """
    Used by ML smoketests.
    """
    return pytestconfig.getoption("--model-name")


@pytest.fixture
def deployment_base_url(pytestconfig):
    """
    Used by ML smoketests.
    """
    return pytestconfig.getoption("--deployment-base-url")


@pytest.fixture
def sdk_version(pytestconfig):
    """
    Used by ML smoketests.
    """
    return pytestconfig.getoption("--sdk-version")


@pytest.fixture
def prediction_input():
    """
    Used by ML smoketests.
    """
    return {"inputs": [{"features": {"age": 20}}, {"features": {"age": 40}}]}


@pytest.fixture
def prediction_output():
    """
    Used by ML smoketests.
    """
    return ["no", "yes"]
