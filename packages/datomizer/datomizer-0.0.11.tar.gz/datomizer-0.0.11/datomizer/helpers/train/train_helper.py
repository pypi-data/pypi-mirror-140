import json
import requests
from datomizer import DatoMapper
from datomizer.utils import constants, general


def create_train_request(should_evaluate=True) -> dict:
    return {"sampleInputData": 1, "privacyLevels": [-1], "shouldEvaluate": should_evaluate}


def train(dato_mapper: DatoMapper, should_evaluate=True) -> int:
    dato_mapper.wait()
    response_json = dato_mapper.datomizer.get_response_json(requests.put,
                                                            url=constants.MANAGEMENT_PUT_TRAIN_FLOW,
                                                            url_params=[dato_mapper.business_unit_id,
                                                                        dato_mapper.project_id,
                                                                        dato_mapper.flow_id],
                                                            headers={"Content-Type": "application/json"},
                                                            data=json.dumps(create_train_request(should_evaluate)))
    return response_json


def get_train_iteration(dato_mapper: DatoMapper, train_id) -> dict:
    flow = dato_mapper.get_flow()
    iteration = [t for t in flow[general.TRAIN_ITERATIONS] if t[general.ID] == train_id][0]
    return iteration


def get_train_generated_zip(dato_mapper: DatoMapper, train_id: int) -> str:
    response_json = dato_mapper.datomizer.get_response_json(requests.get,
                                                            url=constants.MANAGEMENT_GET_GENERATED_DATA,
                                                            url_params=[dato_mapper.business_unit_id,
                                                                        dato_mapper.project_id,
                                                                        dato_mapper.flow_id, train_id])
    return response_json[general.URL]
