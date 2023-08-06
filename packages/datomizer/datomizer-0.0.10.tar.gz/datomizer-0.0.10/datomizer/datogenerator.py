import io

from datomizer import DatoTrainer
from datomizer.helpers import common_helper
from datomizer.helpers.generator import generator_helper
from datomizer.helpers.datasource import datasource_helper
from datomizer.utils import general, step_types


class DatoGenerator(object):
    dato_trainer: DatoTrainer
    synth_id: int
    datasource_id: int

    def __init__(self, dato_trainer: DatoTrainer):
        self.validate_trainer(dato_trainer)
        self.synth_id = 0
        self.datasource_id = 0

    @classmethod
    def restore(cls, dato_trainer: DatoTrainer, synth_id):
        dato_generator = cls(dato_trainer)
        dato_generator.synth_id = synth_id
        dato_generator.wait()
        return dato_generator

    def validate_trainer(self, dato_trainer: DatoTrainer) -> None:
        if not (dato_trainer.train_id > 0 and dato_trainer.train_id > 0 and dato_trainer.model_id > 0):
            raise Exception("DatoTrainer is not valid")
        self.dato_trainer = dato_trainer

    def get_flow(self) -> dict:
        if not (self.dato_trainer.dato_mapper.business_unit_id > 0 and
                self.dato_trainer.dato_mapper.project_id > 0 and
                self.synth_id > 0):
            return
        return common_helper.get_flow(datomizer=self.dato_trainer.dato_mapper.datomizer,
                                      business_unit_id=self.dato_trainer.dato_mapper.business_unit_id,
                                      project_id=self.dato_trainer.dato_mapper.project_id,
                                      flow_id=self.synth_id,
                                      is_synth=True)

    def create_datasource(self) -> None:
        if self.datasource_id > 0:
            return
        self.datasource_id = datasource_helper.create_target_private_datasource(self.dato_trainer.dato_mapper.datomizer)

    def generate(self, wait=True) -> None:
        self.create_datasource()
        if self.synth_id > 0:
            return
        self.synth_id = generator_helper.generate(self.dato_trainer, self.datasource_id)
        if wait:
            self.wait()

    def wait(self) -> None:
        if not (self.synth_id > 0):
            raise Exception("Synth not configured")
        status = common_helper.wait_for_step_type(datomizer=self.dato_trainer.dato_mapper.datomizer,
                                                  business_unit_id=self.dato_trainer.dato_mapper.business_unit_id,
                                                  project_id=self.dato_trainer.dato_mapper.project_id,
                                                  flow_id=self.synth_id,
                                                  is_synth=True,
                                                  step_type=step_types.GENERATE)
        if status == general.ERROR:
            raise Exception("Synth Failed")
        self.datasource_id = self.get_flow()[general.TARGET_DATASOURCE_ID]

    def get_generated_data(self) -> None:
        if not (self.synth_id > 0):
            return
        print(common_helper.get_generated_zip(datomizer=self.dato_trainer.dato_mapper.datomizer,
                                              business_unit_id=self.dato_trainer.dato_mapper.business_unit_id,
                                              project_id=self.dato_trainer.dato_mapper.project_id,
                                              flow_id=self.synth_id))

    def get_generated_data_csv(self, table_name: str = None) -> io.StringIO:
        if not (self.synth_id > 0):
            return

        tables = [table['name'] for table in self.dato_trainer.dato_mapper.schema['tables']]
        if table_name not in tables:
            table_name = tables[0]

        return common_helper.get_generated_csv(datomizer=self.dato_trainer.dato_mapper.datomizer,
                                               business_unit_id=self.dato_trainer.dato_mapper.business_unit_id,
                                               project_id=self.dato_trainer.dato_mapper.project_id,
                                               flow_id=self.synth_id,
                                               table_name=table_name)
