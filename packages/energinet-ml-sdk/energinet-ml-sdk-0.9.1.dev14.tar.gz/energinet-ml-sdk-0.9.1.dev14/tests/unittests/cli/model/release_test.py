# import os
# from pathlib import Path
#
# import pydantic
# import pytest
# import tempfile
# from click.testing import CliRunner
# from unittest.mock import patch, Mock, ANY
#
# from energinetml.core.model import Model, TrainedModel
# from energinetml.core.project import Project
# from energinetml.cli.model.release import release
#
#
# # Project
# PROJECT_NAME = 'NAME'
# SUBSCRIPTION_ID = 'SUBSCRIPTION-ID'
# RESOURCE_GROUP = 'RESOURCE-GROUP'
# WORKSPACE_NAME = 'WORKSPACE-NAME'
#
#
# # Model
# MODEL_NAME = 'NAME'
# EXPERIMENT = 'EXPERIMENT'
# COMPUTE_TARGET = 'COMPUTE-TARGET'
# VM_SIZE = 'VM-SIZE'
# DATASETS = ['iris', 'hades:2']
# FEATURES = ['feature1', 'feature2']
# PARAMETERS = {'param1': 'value1', 'param2': 'value2'}
#
#
# @pytest.fixture
# def model_path():
#     with tempfile.TemporaryDirectory() as path:
#         project = Project.create(
#             path=path,
#             name=PROJECT_NAME,
#             subscription_id=SUBSCRIPTION_ID,
#             resource_group=RESOURCE_GROUP,
#             workspace_name=WORKSPACE_NAME,
#         )
#
#         model_path = project.default_model_path(MODEL_NAME)
#
#         model = Model.create(
#             path=model_path,
#             name=MODEL_NAME,
#             experiment=EXPERIMENT,
#             compute_target=COMPUTE_TARGET,
#             vm_size=VM_SIZE,
#             datasets=DATASETS,
#             features=FEATURES,
#             parameters=PARAMETERS,
#         )
#
#         TrainedModel(
#             model='123',  # Just not None
#             params={'asd': 123},
#         ).dump(model.trained_model_path)
#
#         yield model_path
#
#
# # -- Tests -------------------------------------------------------------------
#
#
# def test__model_predict__no_json_provided__should_abort(model_path):
#     """
#     :param str model_path:
#     """
#     runner = CliRunner()
#
#     # Act
#     result = runner.invoke(
#         cli=predict,
#         args=['--path', model_path],
#     )
#
#     # Assert
#     assert result.exit_code == 1
#     assert result.output.startswith((
#         'You must provide me with either the -j/--json '
#         'or the -f/--json-file parameter'
#     ))
