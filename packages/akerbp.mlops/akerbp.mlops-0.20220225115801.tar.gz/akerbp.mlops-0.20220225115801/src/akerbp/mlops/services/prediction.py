"""
service.py

Prediction service. 
"""
import uuid
import json
from importlib import import_module

from akerbp.mlops import __version__ as version
from akerbp.mlops.core import config, logger
import akerbp.mlops.cdf.helpers as mlops_helpers
from cognite.client.exceptions import CogniteNotFoundError

c = config.read_service_settings()
model_module = import_module(c.model_import_path)
predict = model_module.predict
_initialization = model_module.initialization
ModelException = model_module.ModelException

logging=logger.get_logger("mlops_services")

logging.debug(f"MLOps framework version {version}")


def initialization(secrets):
    """
    Read initialization object required by `predict`
    """
    # This check adds a little overhead to each prediction
    if 'init_object' not in globals():
        global init_object
        artifact_folder = c.artifact_folder
        init_object = _initialization(artifact_folder, secrets)
        logging.debug(f"Loaded initialization object")


def service(data, secrets):
    """
    Generate prediction for an input
    Inputs:
        data: input to the model (sent by a user through the API)
        secrets: api keys that the model may need during initialization
    Output:
        Dictionary with a status field ('ok' or 'error'). If status is 'ok', 
         there is a 'prediction' field as well. If status is 'error', there is 
         a 'message' field as well.
    """
    try:
        initialization(secrets)
        y = predict(data, init_object, secrets)
        if data["to_file"]:
            mlops_helpers.api_keys = secrets 
            mlops_helpers.set_up_cdf_client()
            cdf_client = mlops_helpers.global_client
            external_file_id = f"{c.model_name}_predictions_{uuid.uuid4().hex}.binary"
            try: 
                cdf_client["files"].files.delete(external_id=external_file_id)
            except CogniteNotFoundError:
                pass
            cdf_client["files"].files.upload_bytes(
                content=str(json.dumps(y)), name=f"{c.model_name}_predictions", external_id=external_file_id
            )
            return dict(status="ok", prediction=False, prediction_file=external_file_id, model_id=c.model_id)
        else:
            return dict(status="ok", prediction=y,prediction_file=False, model_id=c.model_id)
    except ModelException as error:
        error_message = f"Could not get a prediction. Message: {error}"
        logging.error(error_message)
        return dict(status="error", message=error_message, model_id=c.model_id)
