import requests
import json
from typing import Union
import ast

from external_services.API_KEYS import PERENUAL_API_KEY as API_KEY


# default_include = ('current', 'minutely', 'hourly', 'daily')
# api_include = ('current', 'minutely', 'hourly', 'daily', 'alerts')


# ----- UTILITY ----- #
def _collection_to_string(collection: Union[list, tuple]):  # this function is useless
    ret_str = ''
    for item in collection:
        ret_str += str(item) + ','
    ret_str = ret_str.removesuffix(',')
    return ret_str


# ----- API ----- #
def get_species(species_name) -> dict:
    url = f"https://perenual.com/api/species-list?key={API_KEY}&q={species_name}"
    species_data = json.loads(requests.get(url).text)
    return species_data


def get_species_details(idx):
    url = f"https://perenual.com/api/species/details/{idx}?key={API_KEY}"
    species_details = json.loads(requests.get(url).text)
    return species_details


if __name__ == '__main__':
    data = get_species('Tomato')
    for plant in data['data']:
        print(plant['common_name'])
