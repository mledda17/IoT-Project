import requests
import json
from typing import Union
import ast

from external_services.API_KEYS import TREFLE_API_KEY as API_KEY


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
    url = f"https://trefle.io/api/v1/species/search?token={API_KEY}&q={species_name}"
    species_data = json.loads(requests.get(url).text)
    return species_data


def get_species_by_id(idx):
    url = f"https://trefle.io/api/v1/species/{idx}?token={API_KEY}"
    species_details = json.loads(requests.get(url).text)
    return species_details


if __name__ == '__main__':
    print(get_species_by_id(263689))
