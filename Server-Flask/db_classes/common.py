from enum import Enum
import string


class WateringFrequency(Enum):
    DAILY = 1
    EVERY_TWO_DAYS = 2
    EVERY_THREE_DAYS = 3
    EVERY_FOUR_DAYS = 4
    EVERY_FIVE_DAYS = 5
    EVERY_SIX_DAYS = 6
    WEEKLY = 7


# Function to convert the Enum into a list of choices
def get_watering_frequency_choices():
    choices = []
    for frequency in WateringFrequency:
        # Convert the enum member to a tuple (value, readable name)
        readable_name = frequency.name.replace("_", " ").capitalize()
        choices.append((frequency.value, readable_name))
    return choices


if __name__ == '__main__':
    print(get_watering_frequency_choices())

