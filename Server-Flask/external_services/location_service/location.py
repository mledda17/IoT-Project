"""
Interface file to abstract location_service services
"""
from geopy import location

# ----- LOCATION SERVICES ----- #

from external_services.location_service._bing import geolocator


def search_location(locality: str) -> location:
    """
    :param locality:
    :return: a geolocator location type
    """
    return geolocator.geocode(locality)


def search_address(locality: str) -> str:
    """
    :param locality:
    :return: an actual address
    """
    locations = geolocator.geocode(locality, exactly_one=False)
    return [loc.address for loc in locations] if location else []


def search_coordinates(locality: str) -> tuple:
    """
    :param locality:
    :return: an actual address
    """
    actual_locality = geolocator.geocode(locality)
    return actual_locality.latitude, actual_locality.longitude



# ----- TEST ----- #

if __name__ == "__main__":
    print(search_address("Via Marche 36"))
