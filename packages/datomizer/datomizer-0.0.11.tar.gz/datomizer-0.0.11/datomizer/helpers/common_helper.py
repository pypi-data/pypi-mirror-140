import io

import requests
import time
from datomizer import Datomizer
from datomizer.utils import constants, step_types, general


def get_flow(datomizer: Datomizer,
             business_unit_id: str, project_id: str, flow_id: str, is_synth=False) -> dict:

    url = constants.MANAGEMENT_GET_SYNTH_FLOW if is_synth else constants.MANAGEMENT_GET_GENERATIVE_FLOW
    return datomizer.get_response_json(requests.get,
                                       url=url,
                                       url_params=[business_unit_id, project_id, flow_id])


def get_flow_step_status(datomizer: Datomizer,
                         business_unit_id: str, project_id: str, flow_id: str, is_synth=False,
                         step_type: str = '', train_id: int = 0) -> str:
    response_json = get_flow(datomizer, business_unit_id, project_id, flow_id, is_synth)
    return get_relevant_steps_status(response_json, step_type, train_id)


def get_relevant_steps_status(response_json: {}, step_type: str = '', train_id: int = 0) -> str:
    if train_id > 0:
        steps = [iteration for iteration in response_json[general.TRAIN_ITERATIONS]
                 if iteration[general.ID] == train_id][0][general.STEPS]
    else:
        steps = [step for step in response_json[general.STEPS]]

    return get_steps_status(steps, step_type)


def get_steps_status(steps: [], step_type) -> str:
    for step in steps:
        for task in step['tasks']:
            if task['taskStatus'] == general.ERROR:
                return general.ERROR
            if step["stepType"] == step_type:
                return task['taskStatus']

    return general.INITIALIZING


def wait_for_step_type(datomizer: Datomizer,
                       business_unit_id: str, project_id: str, flow_id: str, is_synth=False,
                       step_type: str = '', train_id: int = 0) -> str:
    status = get_flow_step_status(datomizer, business_unit_id, project_id, flow_id, is_synth, step_type, train_id)
    while status in [general.INITIALIZING, general.IN_PROGRESS]:
        time.sleep(10)
        status = get_flow_step_status(datomizer, business_unit_id, project_id, flow_id, is_synth, step_type, train_id)
    return status


def get_generated_zip(datomizer: Datomizer,
                      business_unit_id: int, project_id: int, flow_id: int,
                      train_id: int = 0) -> str:
    response_json = datomizer.get_response_json(requests.get,
                                                url=constants.MANAGEMENT_GET_GENERATED_DATA,
                                                url_params=[business_unit_id, project_id, flow_id, train_id])
    return response_json[general.URL]


def get_generated_csv(datomizer: Datomizer,
                      business_unit_id: int, project_id: int, flow_id: int,
                      table_name: str = "") -> io.StringIO:
    response_json = datomizer.get_response_json(requests.get,
                                                url=constants.MANAGEMENT_GET_GENERATED_CSV,
                                                url_params=[business_unit_id, project_id, flow_id, table_name])
    csv_response = requests.get(response_json[general.URL]).content

    return io.StringIO(csv_response.decode('utf-8'))
