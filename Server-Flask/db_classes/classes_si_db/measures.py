from mongoengine import EmbeddedDocument
from mongoengine import StringField, ListField, EmbeddedDocumentField, BooleanField, DateTimeField, FloatField
from bson import json_util
import json
from datetime import datetime


class Measure(EmbeddedDocument):
    name = StringField(required=True)
    date = DateTimeField(default=datetime.now())
    value = FloatField(required=True)
    unit_of_measure = StringField(required=True)

    @classmethod
    def create_measure(cls, name, value, unit_of_measure):
        return cls(name=name, date=datetime.now(), value=value,
                   unit_of_measure=unit_of_measure)


class Watering(EmbeddedDocument):
    happened = BooleanField(required=True)
    date = DateTimeField(default=datetime.now())

    @classmethod
    def create_watering_record(cls, watering_bool: bool):
        return cls(date=datetime.now(), happened=watering_bool)
