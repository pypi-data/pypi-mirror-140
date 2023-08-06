from datomizer import DatoMapper
from datomizer.helpers import common_helper
from datomizer.helpers.train import train_helper
from datomizer.utils import general, step_types


class DatoTrainer(object):
    dato_mapper: DatoMapper
    train_id: int

    def __init__(self, dato_mapper: DatoMapper):
        self.validate_mapper(dato_mapper)
        self.train_id = 0
        self.model_id = 0
        self.evaluate = True

    @classmethod
    def restore(cls, dato_mapper: DatoMapper, train_id):
        dato_trainer = cls(dato_mapper)
        dato_trainer.train_id = train_id
        dato_trainer.wait()
        return dato_trainer

    def validate_mapper(self, dato_mapper: DatoMapper) -> None:
        if not (dato_mapper.business_unit_id > 0 and dato_mapper.project_id > 0 and dato_mapper.flow_id > 0
                and dato_mapper.schema):
            raise Exception("DatoMapper is not valid")
        self.dato_mapper = dato_mapper

    def train(self, should_evaluate=True, wait=True) -> None:
        if self.train_id > 0:
            return
        self.train_id = train_helper.train(self.dato_mapper, should_evaluate)
        self.evaluate = should_evaluate
        if wait:
            self.wait()

    def wait(self) -> None:
        if not (self.train_id > 0):
            raise Exception("Trainer not configured")
        status = common_helper.wait_for_step_type(datomizer=self.dato_mapper.datomizer,
                                                  business_unit_id=self.dato_mapper.business_unit_id,
                                                  project_id=self.dato_mapper.project_id,
                                                  flow_id=self.dato_mapper.flow_id,
                                                  step_type=step_types.EVALUATE if self.evaluate else step_types.TRAIN,
                                                  train_id=self.train_id)
        if status == general.ERROR:
            raise Exception("Trainer Failed")
        self.model_id = train_helper.get_train_iteration(self.dato_mapper, self.train_id)[general.MODELS][0][general.ID]

    def get_generated_data(self) -> None:
        if not (self.train_id > 0 and self.evaluate):
            return

        print(common_helper.get_generated_zip(datomizer=self.dato_mapper.datomizer,
                                              business_unit_id=self.dato_mapper.business_unit_id,
                                              project_id=self.dato_mapper.project_id,
                                              flow_id=self.dato_mapper.flow_id,
                                              train_id=self.train_id))
