"""
Interface file to abstract weather service services
"""
from external_services.weather_service._openweathermap import get_forecast as gf


# ----- INTERFACES ----- #

class WeatherState:
    def __init__(self, temperature, humidity, weather, longitude=None, latitude=None, country=None):
        self.temperature = temperature
        self.humidity = humidity
        self.weather = weather
        self.longitude = longitude
        self.latitude = latitude
        self.country = country

    def __str__(self):
        return_str = f"Location: coordinates (lat, lon): {self.latitude}, {self.longitude}, " \
            if self.longitude is not None and self.latitude is not None else ""
        return_str += f"Country: {self.country} <---> " if self.country is not None else ""
        return_str += f"Weather: {self.weather}, Temperature: {self.temperature}°C, Humidity: {self.humidity}%"
        return return_str


def get_current_weather(latitude: float, longitude: float) -> WeatherState:
    """
    A function to get the current weather, given a couple of coordinates
    :param latitude:
    :param longitude:
    :return: A WeatherState object containing at least a temperature (C), a weather (Clear, Rainy, ...)
    and a humidity (%)
    """
    weather_dict = gf(latitude=latitude, longitude=longitude)
    return WeatherState(temperature=weather_dict['temperature'], humidity=weather_dict['humidity'],
                        weather=weather_dict['weather'], latitude=weather_dict['longitude'],
                        longitude=weather_dict['latitude'], country=weather_dict['country_code'])


# ------ TEST ------ #

if __name__ == '__main__':
    print(get_current_weather(39.292, 9))  # how cool, it works
