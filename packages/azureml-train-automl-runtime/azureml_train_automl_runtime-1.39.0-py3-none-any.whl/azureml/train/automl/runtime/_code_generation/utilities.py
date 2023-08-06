# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Code gen related utility methods."""
import logging
from typing import Any, Optional, Tuple

from azureml._base_sdk_common._docstring_wrapper import module_logger as experimental_logger
from azureml.core import Run
from azureml.training.tabular import VERSION

from azureml.automl.core import _codegen_utilities
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.train.automl._constants_azureml import RunState
from azureml.train.automl.runtime._code_generation import code_generator, notebook_generator
from azureml.train.automl.runtime._code_generation.constants import CodeGenConstants

logger = logging.getLogger(__name__)


def generate_model_code_and_notebook(current_run: Run, pipeline: Optional[Any] = None) -> None:
    """
    Given a child run, generate the code and notebook for the outputted model and upload them as artifacts.
    """
    # Disable propagation for @experimental attribute during code gen because it can be noisy.
    should_propagate = experimental_logger.propagate
    try:
        experimental_logger.propagate = False
        logger.info("Generating code for the trained model.")
        code = code_generator.generate_full_script(current_run, pipeline)

        with open(CodeGenConstants.ScriptFilename, "w") as f:
            f.write(code)

        current_run.upload_file(CodeGenConstants.ScriptOutputPath, CodeGenConstants.ScriptFilename)
        logger.info(f"Script has been generated, output saved to {CodeGenConstants.ScriptOutputPath}")

        Contract.assert_value(current_run.parent, "parent")
        notebook = notebook_generator.generate_script_run_notebook(
            current_run, environment=current_run.get_environment()
        )
        with open(CodeGenConstants.ScriptRunNotebookFilename, "w") as f:
            f.write(notebook)
        current_run.upload_file(
            CodeGenConstants.ScriptRunNotebookOutputPath, CodeGenConstants.ScriptRunNotebookFilename
        )
        logger.info(f"Notebook has been generated, output saved to {CodeGenConstants.ScriptRunNotebookOutputPath}")

        try:
            # Quickly check for errors in the script
            _codegen_utilities.check_code_syntax(code)
        except Exception as e:
            logging_utilities.log_traceback(e, logger)
            logger.warning(
                "Code generation encountered an error when checking output. The generated code may "
                "require some manual editing to work properly."
            )

        try:
            dependencies = current_run.get_environment().python.conda_dependencies
            dependencies.add_pip_package(f"azureml-training-tabular=={VERSION}.*")
            dependencies.save(CodeGenConstants.CondaEnvironmentFilename)
            current_run.upload_file(
                CodeGenConstants.CondaEnvironmentOutputPath, CodeGenConstants.CondaEnvironmentFilename
            )
            logger.info(
                f"Environment YAML has been generated, output saved to {CodeGenConstants.CondaEnvironmentOutputPath}"
            )
        except Exception as e:
            logging_utilities.log_traceback(e, logger)
            logger.warning("Code generation failed to generate environment file.")

        current_run.set_tags({CodeGenConstants.TagName: RunState.COMPLETE_RUN})
    except Exception as e:
        logging_utilities.log_traceback(e, logger)
        logger.warning("Code generation failed; skipping.")
        current_run.set_tags({CodeGenConstants.TagName: RunState.FAIL_RUN})
    finally:
        experimental_logger.propagate = should_propagate


def get_input_datasets(parent_run: Run) -> Tuple[str, Optional[str]]:
    """
    Given a parent run, fetch the IDs of the training and validation datasets, if present.

    :param parent_run: the run to fetch IDs from
    :return: a tuple of (training, validation) dataset IDs
    """
    parent_run_details = parent_run.get_details()
    input_datasets = parent_run_details.get("inputDatasets", [])
    training_dataset_id = None
    validation_dataset_id = None

    for input_dataset in input_datasets:
        consumption_block = input_dataset.get("consumptionDetails", {})
        dataset_name = consumption_block.get("inputName", None)

        if dataset_name == "training_data":
            training_dataset_id = input_dataset["dataset"].id
        elif dataset_name == "validation_data":
            validation_dataset_id = input_dataset["dataset"].id

    assert training_dataset_id is not None, "No training dataset found"
    return training_dataset_id, validation_dataset_id
