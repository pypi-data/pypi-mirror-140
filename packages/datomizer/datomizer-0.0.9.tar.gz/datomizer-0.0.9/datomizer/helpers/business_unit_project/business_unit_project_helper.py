import requests
from datomizer import Datomizer
from datomizer.utils import constants, general
from typing import Tuple


def get_default_business_unit_project(datomizer: Datomizer) -> Tuple[int, int]:
    business_units = datomizer.get_response_json(method=requests.get,
                                                 url=constants.MANAGEMENT_GET_ALL_BUSINESS_UNIT_URL)

    return business_units[0][general.ID], business_units[0]['projects'][0][general.ID]
