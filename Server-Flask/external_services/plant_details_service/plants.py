"""
Interface file to abstract weather service services
"""
from external_services.plant_details_service._trefle import get_species as gs
from external_services.plant_details_service._trefle import get_species_by_id as gsid
import numpy as np

# ----- INTERFACES ----- #


class PlantState:
    def __init__(self, common_name, scientific_name, light, atmospheric_humidity, atmospheric_temperature,
                 soil_humidity, default_image):
        self.common_name = common_name
        self.scientific_name = scientific_name
        self.light = light
        self.atmospheric_humidity = atmospheric_humidity
        self.atmospheric_temperature = atmospheric_temperature
        self.soil_humidity = soil_humidity
        self.ideal_watering = self.calculate_ideal_watering()
        self.default_image = default_image

    def calculate_ideal_watering(self):
        # Normalize parameters (these ranges are examples, adjust as necessary)
        normalized_light = min(max(self.light / 100, 0), 1)  # Light as humidity
        normalized_humidity = min(max(self.atmospheric_humidity / 100, 0), 1)  # Humidity as a percentage
        normalized_temperature = min(max((self.atmospheric_temperature - 10) / 20, 0),
                                     1)  # Assuming temperature ranges from 10 to 30 Celsius
        normalized_soil_humidity = min(max(self.soil_humidity / 100, 0), 1)  # Soil humidity as a percentage

        # Weighted sum of normalized parameters
        score = 0.25 * normalized_light + 0.25 * (1 - normalized_humidity) + 0.25 * normalized_temperature + 0.25 * (
                    1 - normalized_soil_humidity)

        # Map score to 1-7 scale
        ideal_watering = round(1 + 6 * score)

        return ideal_watering

    def __str__(self):
        pass

    def normalize(self, par, max_val):
        return par / max_val

    def to_dict(self):
        return {
            "scientific_name": self.scientific_name,
            "light": self.light,
            "atmospheric_humidity": self.atmospheric_humidity,
            "atmospheric_temperature": self.atmospheric_temperature,
            "soil_humidity": self.soil_humidity,
            "ideal_watering": self.ideal_watering,
            "default_image": self.default_image
        }


def get_species_common_names(species_name):
    species_data = get_species(species_name)
    common_names = []

    # Extracting the common names from the species data
    for species in species_data['data']:
        if 'common_name' in species and species['common_name']:
            common_names.append(species['common_name'])

    return common_names


def get_species(species_name):
    species_dict = gs(species_name)
    #print(species_dict)
    return species_dict


def get_id_from_species_name(species_name):
    species_id = gs(species_name)['data'][0]['id']
    return species_id


def get_species_details(species_name):
    idx = get_id_from_species_name(species_name)
    species_details = gsid(idx)
    return species_details


def get_default_value_or_transform(value, default, transform=lambda x: x):
    return transform(value) if value is not None else default


def get_species_fields(species_name) -> PlantState:
    species_dict = get_species_details(species_name)['data']
    growth = species_dict['growth']

    light = get_default_value_or_transform(growth['light'], 5000, lambda x: x * 10)
    atm_humidity = get_default_value_or_transform(growth['atmospheric_humidity'], 60.0, lambda x: x * 10)
    atm_min_temp = get_default_value_or_transform(growth['minimum_temperature']['deg_c'], 25.0)
    atm_max_temp = get_default_value_or_transform(growth['maximum_temperature']['deg_c'], 25.0)
    soil_humidity = get_default_value_or_transform(growth['soil_humidity'], 50.0, lambda x: x * 10)

    atm_temp = float((atm_min_temp + atm_max_temp) / 2)

    return PlantState(common_name=species_dict['common_name'], scientific_name=species_dict['scientific_name'],
                      light=light, atmospheric_humidity=atm_humidity, atmospheric_temperature=atm_temp,
                      soil_humidity=soil_humidity, default_image=species_dict['image_url']).to_dict()


if __name__ == '__main__':
    plant = get_species_fields('Tuna')
    print(plant)
