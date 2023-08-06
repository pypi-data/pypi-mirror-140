import json
import requests
from datomizer import DatoTrainer
from datomizer.utils import constants, general


def create_synth_request(dato_trainer: DatoTrainer, datasource_id: int = general.NEW_PRIVATE_ID) -> dict:
    return {
        "title": "Synth SDK",
        "datasourceId": datasource_id,
        "sizeInGB": 0,
        "outputRatio": 1,
        "modelId": dato_trainer.model_id,
        "synthStrategy": general.SPARK_WRITE_OPTIONS_OVERWRITE
    }


def generate(dato_trainer: DatoTrainer, datasource_id: int) -> int:
    dato_trainer.wait()
    response_json = dato_trainer.dato_mapper.datomizer.get_response_json(
        requests.put,
        url=constants.MANAGEMENT_PUT_SYNTH_FLOW,
        url_params=[dato_trainer.dato_mapper.business_unit_id,
                    dato_trainer.dato_mapper.project_id,
                    dato_trainer.dato_mapper.flow_id],
        headers={"Content-Type": "application/json"},
        data=json.dumps(create_synth_request(dato_trainer, datasource_id)))
    return response_json[general.ID]
