from hashlib import sha256
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz


def hash_string(str_var: str):
    return sha256(str_var.encode('utf-8'))


class UserMustLoggedException(Exception):
    def __init__(self, message):
        if message is not None:
            self.message = "To perform this action: " + message + "user must logged in!"
        else:
            self.message = "User must logged in to perform such an action"
        super().__init__(self.message)


def get_current_time(latitude, longitude):
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lat=latitude, lng=longitude)

    if timezone_str is None:
        return None

    timezone = pytz.timezone(timezone_str)
    current_time = datetime.now(timezone)
    time_str = current_time.strftime('%H:%M')
    data = time_str.split(':')
    return data[0], data[1]



if __name__ == "__main__":
    from external_services.location_service.location import search_coordinates

    latitude, longitude = search_coordinates("new york")
    print(get_current_time(latitude, longitude))
