import requests
from typing import Union
import ast
import json

from external_services.API_KEYS import OPEN_WEATHER_MAP_API_KEY as API_KEY


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
def get_forecast_raw(latitude, longitude) -> dict:
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={API_KEY}&units=metric"
    weather = json.loads(requests.get(url).text)
    return weather


def get_forecast(latitude: float, longitude: float) -> dict:
    current_weather = get_forecast_raw(latitude, longitude)
    return {'temperature': current_weather['main']['temp'],
            'humidity': current_weather['main']['humidity'],
            'weather': current_weather['weather'][0]['main'],
            'longitude': current_weather['coord']['lon'],
            'latitude': current_weather['coord']['lat'],
            'country_code': current_weather['sys']['country']
            }


# ----- TEST ----- #

if __name__ == '__main__':
    print(get_forecast_raw(20, 30))
    print(get_forecast(20, 30))
