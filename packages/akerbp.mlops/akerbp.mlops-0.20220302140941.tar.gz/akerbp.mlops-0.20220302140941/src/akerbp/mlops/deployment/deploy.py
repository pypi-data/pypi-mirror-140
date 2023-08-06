"""
deploy.py

Deploy services in either Google Cloud Run or CDF Functions. 
Model registry uses CDF Files.
""" 
import os
import sys
import json
import traceback
import subprocess
from pathlib import Path

import akerbp.mlops.model_manager as mm
from akerbp.mlops.deployment import helpers, platforms
from akerbp.mlops.core import logger, config
from akerbp.mlops.cdf import helpers as cdf
logging=logger.get_logger(name='mlops_deployment')


platform_methods = platforms.get_methods()


def deploy_model(model_settings, platform_methods=platform_methods):
    """
    Deploy a model.

    This will create a deployment folder and change current working directory 
    to it.

    Input:
        - model_settings: (ServiceSettings) settings for the model service
        - platform_methods: (dictionary) where key is the platform and value
            is a tuple with deploy and test functions.
    """
    try:            
        c = model_settings
        env = config.envs.env
        service_name = config.envs.service_name
        deployment_folder = helpers.deployment_folder_path(c.model_name)
        function_name = f"{c.model_name}-{service_name}-{env}"
        human_readable_function_name = c.human_friendly_model_name

        logging.debug(" ")
        logging.info(f"Starting deployment of model {c.human_friendly_model_name} with external id {function_name}")

        if (service_name == 'prediction') and c.artifact_folder:
            mm.set_active_dataset(c.dataset)
            c.model_id = mm.set_up_model_artifact(c.artifact_folder, c.model_name)

        logging.info("Create deployment folder and move required files/folders")
        deployment_folder.mkdir()
        helpers.copy_to_deployment_folder(c.files, deployment_folder)

        logging.debug(f"cd {deployment_folder}")
        os.chdir(deployment_folder)
        helpers.set_up_requirements(c)
        config.store_service_settings(c)

        logging.info(f"Run model and service tests")
        if c.test_file:
            # It should be run as an independent process so that the right
            # packages are imported, the import paths are correct, etc. 
            command = [sys.executable, "-m", 
                        "akerbp.mlops.services.test_service"]
            output = subprocess.check_output(command, encoding='UTF-8')
            model_input = json.loads(output.splitlines()[-1])
        else:
            logging.warning("Model test file is missing! Didn't run tests")

        if c.platform == "cdf": # For now this will always be the case
            if len(splitted_external_id := function_name.split("-")) > 3: 
                latest_model_version = splitted_external_id[-1]
                env = splitted_external_id[-2]
            else: 
                env = splitted_external_id[-1]
            model_name = splitted_external_id[0]

            artifact_external_id = model_name + "/" + env 
            artifact_versions = cdf.query_file_versions(directory_prefix="/mlops", external_id_prefix=artifact_external_id)
            if len(artifact_versions) == 0: 
                latest_artifact_version = 1
            else:
                latest_artifact_version = artifact_versions.loc[artifact_versions.uploadedTime.argmax()].metadata["version"]
            logging.info(f"Latest artifact version in {env} environment is {latest_artifact_version}")
            external_id = function_name + "-" + str(latest_artifact_version)
        else: 
            external_id = function_name 

        logging.info(f"Deploying function {human_readable_function_name} with external id {external_id} to {c.platform}")
        deploy_function, test_function = platform_methods[c.platform]
        deploy_function(human_readable_function_name, external_id, info=c.info[service_name])
        
        if c.test_file:
            logging.info("Make a test call")
            test_function(external_id, model_input) 
        else:
            logging.warning("No test file was set up. End-to-end test skipped!")
    
        return "OK"
    except Exception:
        trace = traceback.format_exc()
        return f"Model failed to deploy!\n{trace}"


def deploy(project_settings):
    """
    Deploy a machine learning project that potentially contains multiple models.
    Deploy each model in the settings and make sure that if one model fails it
    does not affect the rest. At the end, if any model failed, it raises an
    exception with a summary of all models that failed.

    Input:
        - Project settings as described by the user
    """
    failed_models = {}
    cwd_path = Path.cwd()
        
    for c in project_settings:
        status = deploy_model(c)
        if status != "OK":
            logging.error(status)
            failed_models[c.human_friendly_model_name] = status
        
        logging.debug(f"cd ..")
        os.chdir(cwd_path)
        helpers.rm_deployment_folder(c.model_name)

    if failed_models:
        for model, message in failed_models.items():
            logging.debug(" ")
            logging.info(f"Model {model} failed: {message}")
        raise Exception("At least one model failed.")


if __name__ == '__main__':
    mm.setup()
    settings = config.read_project_settings()
    deploy(settings)