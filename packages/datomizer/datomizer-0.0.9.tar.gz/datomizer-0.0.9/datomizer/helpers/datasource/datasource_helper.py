import requests
import tempfile
from datomizer import Datomizer
from datomizer.utils import constants, general


def create_origin_private_datasource(datomizer: Datomizer, df, name="temp") -> int:
    if not name.endswith(".csv"):
        name = name + ".csv"
    datasource = datomizer.get_response_json(requests.post, url=constants.MANAGEMENT_POST_ADD_ORIGIN_PRIVATE_DATASOURCE)
    put_presigned_response = datomizer.get_response_json(requests.get,
                                                         url=constants.MANAGEMENT_GET_PUT_PRESIGNED_URL,
                                                         url_params=[datasource[general.ID], name])
    with tempfile.TemporaryDirectory() as temp_dir:
        path = f"{temp_dir}/{name}"
        save_df_to_csv(df, path)
        with open(path, 'r') as temp_file:
            header = {"Content-Type": "text/csv"}
            response = requests.put(url=put_presigned_response[general.URL], data=temp_file, headers=header)
            datomizer.validate_response(response, "Upload to put presigned url")

    return datasource[general.ID]


def create_target_private_datasource(datomizer: Datomizer):
    datasource = datomizer.get_response_json(requests.post, url=constants.MANAGEMENT_POST_ADD_TARGET_PRIVATE_DATASOURCE)
    return datasource[general.ID]


def save_df_to_csv(df, path: str):
    df_type = f"{type(df).__module__}.{type(df).__name__}"
    if df_type == "pandas.core.frame.DataFrame":
        df.to_csv(path)
        return
