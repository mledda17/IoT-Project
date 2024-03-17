import string

# -----   NAMES    ----- #

object_name_max_length = 50
object_name_additional_characters = " _-."
object_name_enabled_characters = string.ascii_letters + string.digits + object_name_additional_characters


def validate_object_name(object_name: str):
    for c in object_name:
        if c not in object_name_enabled_characters:
            return False
    return True

# ----- EXCEPTIONS ----- #


class ObjectCreationException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__("An error occurred when creating an object:\n" + self.message)


class ObjectModifyException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__("An error during the update of the pot has occurred: \n"+self.message)


class ObjectNameTooLongException(ObjectCreationException):
    def __init__(self, object_name):
        self.message = ("The name of the object is too long (max length: " + str(object_name_max_length) +
                        ", actual length: " + str(len(object_name)) + ")")
        super().__init__(self.message)


class InvalidObjectNameException(ObjectCreationException):
    def __init__(self, message=None):
        if message is None:
            self.message = ("The object name can contains only letters, numbers and "
                            + object_name_additional_characters)
        else:
            self.message = message
        super().__init__(self.message)