from mongoengine import Document, StringField, DictField, DateTimeField, ListField, SequenceField, DateTimeField
from mongoengine import EmbeddedDocumentField, FloatField, IntField
from .measures import Measure, Watering
from bson import json_util
import json
from .classes_si_db_common import object_name_max_length, validate_object_name
from .classes_si_db_common import InvalidObjectNameException, ObjectNameTooLongException

MAX_MEASURES_AMOUNT = 120

class SmartPots(Document):
    u_id = SequenceField(collection_name='SmartPots')
    serial_number = StringField(required=True)
    name = StringField()
    creation_date = DateTimeField()
    location = StringField(required=True)

    # Plant data
    plant_name = StringField()
    desired_humidity = FloatField()
    watering_frequency = IntField(required=True)

    # Measures data
    measures = ListField(EmbeddedDocumentField(Measure))

    # Watering cycles
    watering_cycles = ListField(EmbeddedDocumentField(Watering))

    additional_attributes = DictField()
    meta = {'collection': 'SmartPots'}

    def to_dict(self):
        data = self.to_mongo().to_dict()
        return json.loads(json_util.dumps(data))

    def add_measure(self, name, value, unit_of_measurement):
        self.measures.append(Measure.create_measure(name, value, unit_of_measurement))
        sorted_measures = sorted(self.measures, key=lambda x: x.date) # old to new
        if len(sorted_measures) - 1 > MAX_MEASURES_AMOUNT:
            to_delete = sorted_measures[0:len(sorted_measures) - MAX_MEASURES_AMOUNT]
            for to_del in to_delete:
                self.measures.remove(to_del)
        self.save()

    def add_watering_cycle(self, watering_bool):
        self.watering_cycles.append(Watering.create_watering_record(watering_bool))
        sorted_watering = sorted(self.watering_cycles, key=lambda x: x.date)
        if len(sorted_watering) - 1 > MAX_MEASURES_AMOUNT:
            to_delete = sorted_watering[0:len(sorted_watering) - MAX_MEASURES_AMOUNT]
            for to_del in to_delete:
                self.watering_cycles.remove(to_del)
        self.save()


    @classmethod
    def create_pot(cls, serial_number, location, plant_name, desired_humidity, watering_frequency, additional_attributes,
                   name="Unnamed group"):
        if not validate_object_name(name):
            raise InvalidObjectNameException()
        if len(name) > object_name_max_length:
            raise ObjectNameTooLongException(name)
        return SmartPots._loc_create_pot(name=name, serial_number=serial_number, location=location, plant_name=plant_name,
                                         desired_humidity=desired_humidity, watering_frequency=watering_frequency,
                                         additional_attributes=additional_attributes)

    @classmethod
    def _loc_create_pot(cls, serial_number, location, plant_name, desired_humidity, watering_frequency, additional_attributes,
                        name="Unnamed group"):
        pot = cls(name=name, serial_number=serial_number, location=location, plant_name=plant_name, desired_humidity=desired_humidity,
                  watering_frequency=watering_frequency, additional_attributes=additional_attributes)
        pot.save()
        return pot
