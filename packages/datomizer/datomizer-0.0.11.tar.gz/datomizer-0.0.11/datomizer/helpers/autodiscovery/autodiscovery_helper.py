import json
import time
import requests
from datomizer import Datomizer
from datomizer.utils import constants, general


def create_flow_creation_request(datasource_id: int, sample_percent: int = 1, title: str = "new_flow") -> dict:
    return {
        "modelTrainingConfiguration": {
            "title": title,
            "dataSourceId": datasource_id,
            "sampleInputData": sample_percent,
            "privacyLevels": [-1]
        }
    }


def discover(datomizer: Datomizer,
             business_unit_id: str, project_id: str, datasource_id: str,
             sample_percent: int = 1, title: str = "new_flow") -> int:
    flow_creation_request = create_flow_creation_request(datasource_id, sample_percent, title)
    response_json = datomizer.get_response_json(requests.post,
                                                url=constants.MANAGEMENT_POST_ADD_FLOW,
                                                url_params=[business_unit_id, project_id],
                                                headers={"Content-Type": "application/json"},
                                                data=json.dumps(flow_creation_request))
    return response_json[general.ID]


def get_schema_discovery(datomizer: Datomizer,
                         business_unit_id: str, project_id: str, flow_id: str) -> dict:
    response_json = datomizer.get_response_json(requests.get,
                                                url=constants.MANAGEMENT_GET_SCHEMA_DISCOVERY,
                                                url_params=[business_unit_id, project_id, flow_id])
    return response_json

