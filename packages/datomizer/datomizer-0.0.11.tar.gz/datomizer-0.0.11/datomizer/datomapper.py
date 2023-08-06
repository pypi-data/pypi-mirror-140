from datomizer import Datomizer
from datomizer.helpers.datasource import datasource_helper
from datomizer.helpers import common_helper
from datomizer.helpers.business_unit_project import business_unit_project_helper as bu_proj_helper
from datomizer.helpers.autodiscovery import autodiscovery_helper
from datomizer.utils import step_types, general


class DatoMapper(object):
    datomizer: Datomizer
    business_unit_id: int
    project_id: int
    datasource_id: int
    flow_id: int
    schema: {}

    def __init__(self, datomizer: Datomizer):
        if not (datomizer.access_token != ""):
            raise Exception("Datomizer is not valid")
        self.datomizer = datomizer
        self.business_unit_id, self.project_id = bu_proj_helper.get_default_business_unit_project(self.datomizer)
        self.datasource_id = 0
        self.flow_id = 0
        self.schema = {}

    @classmethod
    def restore(cls, datomizer: Datomizer, flow_id):
        dato_mapper = cls(datomizer)
        dato_mapper.flow_id = flow_id
        dato_mapper.wait()
        return dato_mapper

    def get_flow(self) -> dict:
        if not (self.business_unit_id > 0 and self.project_id > 0 and self.flow_id > 0):
            return
        return common_helper.get_flow(self.datomizer, self.business_unit_id, self.project_id, self.flow_id)

    def create_datasource(self, df, name="temp_df") -> None:
        if self.datasource_id > 0:
            return
        self.datasource_id = datasource_helper.create_origin_private_datasource(self.datomizer, df, name)

    def discover(self, df=None, df_name=None, sample_percent: int = 1, title: str = "sdk_flow", wait=True) -> None:
        if df is not None:
            self.create_datasource(df, df_name if df_name else title)
        if not (self.business_unit_id > 0 and self.project_id > 0 and self.datasource_id > 0):
            return
        self.flow_id = autodiscovery_helper.discover(self.datomizer,
                                                     self.business_unit_id, self.project_id, self.datasource_id,
                                                     sample_percent, title)
        if wait:
            self.wait()

    def wait(self) -> None:
        if not (self.business_unit_id > 0 and self.project_id > 0 and self.flow_id > 0):
            raise Exception("Auto Discovery Not Configured")
        status = common_helper.wait_for_step_type(datomizer=self.datomizer,
                                                  business_unit_id=self.business_unit_id,
                                                  project_id=self.project_id,
                                                  flow_id=self.flow_id,
                                                  step_type=step_types.COLUMN_DISCOVERY)
        if status == general.ERROR:
            raise Exception("Auto Discovery Failed")
        self.datasource_id = self.get_flow()[general.ORIGIN_DATASOURCE_ID]
        self.get_schema_discovery()

    def get_schema_discovery(self) -> dict:
        if not (self.business_unit_id > 0 and self.project_id > 0 and self.flow_id > 0):
            return
        if self.schema:
            return self.schema
        self.schema = autodiscovery_helper.get_schema_discovery(self.datomizer,
                                                                self.business_unit_id, self.project_id, self.flow_id)
        return self.schema
