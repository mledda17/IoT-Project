from db_classes.classes_si_db.smartpots import SmartPots
from db_classes.classes_si_db.user import Users
from db_classes.common import WateringFrequency
from utilities.object_management_utilities import assign_pot_to_user


def create_pot_and_assign_to_user(user: Users, serial_number, location, plant_name, desired_humidity, watering_frequency,
                                  additional_attributes, pot_name: str = "Unnamed group", ):
    pot = SmartPots.create_pot(serial_number=serial_number, location=location, plant_name=plant_name, desired_humidity=desired_humidity,
                               watering_frequency=watering_frequency, additional_attributes=additional_attributes,
                               name=pot_name)
    assign_pot_to_user(pot=pot, user=user)
    return pot
