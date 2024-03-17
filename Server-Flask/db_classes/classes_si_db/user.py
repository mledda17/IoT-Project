from mongoengine import Document, StringField, DictField, DateTimeField, ListField, ReferenceField, IntField, \
    SequenceField, EmbeddedDocumentField
from .smartpots import SmartPots
from flask_login import UserMixin
from bson import json_util
from hashlib import sha256
import string
import json

password_max_length = 50
username_max_length = 25

password_enabled_characters = string.printable
username_additional_characters = " _-."
username_enabled_characters = string.ascii_letters + string.digits + username_additional_characters


class Users(Document):
    u_id = StringField(required=True, unique=True) # hash of username
    username = StringField(required=True, unique=True)
    hashed_password = StringField(required=True)
    creation_date = DateTimeField()

    pots = ListField(ReferenceField(SmartPots, reverse_delete_rule=4))
    additional_attributes = DictField()
    meta = {'collection': 'Users'}

    # --- DB MANAGEMENT UTILITIES --- #

    @staticmethod
    def _validate_password(password: str):
        for c in password:
            if c not in password_enabled_characters:
                return False
        return True

    @staticmethod
    def _validate_username(username: str):
        for c in username:
            if c not in username_enabled_characters:
                return False
        return True

    @staticmethod
    def hash_string(plain_string: str):
        return sha256(plain_string.encode('utf-8')).hexdigest()

    def to_dict(self):
        data = self.to_mongo().to_dict()
        return json.loads(json_util.dumps(data))

    @classmethod
    def user_exist(cls, username: str):
        user = cls.objects(username=username).first()
        if user:
            return True
        return False

    @classmethod
    def user_exist_uid(cls, u_id: str):
        user = cls.objects(u_id=u_id).first()
        if user:
            return True
        return False

    @classmethod
    def _loc_create_user(cls, username, hashed_password):
        user = cls(u_id=Users.hash_string(username), username=username, hashed_password=hashed_password)
        user.save()
        return user

    @classmethod
    def create_user(cls, username: str, password: str):
        if not cls._validate_username(username):
            raise InvalidUsernameException()
        if len(username) > username_max_length:
            raise UsernameTooLongException(username)
        if not cls._validate_password(password):
            raise InvalidPasswordException(password)
        if len(password) > password_max_length:
            raise PasswordTooLongException(password)
        if cls.user_exist(username):
            raise UserExistException(username)

        hashed_password = Users.hash_string(password)
        return cls._loc_create_user(username=username, hashed_password=hashed_password)


# ----- FLASK LOGIN OBJECT ----- #

class UserObject(UserMixin):
    def __init__(self, user_mongoengine_query_object):
        self.username = user_mongoengine_query_object.username
        self.password = user_mongoengine_query_object.hashed_password
        self.user_id = user_mongoengine_query_object.u_id

    def get_id(self):
        return str(self.user_id)


# ----- USER CREATION EXCEPTIONS ----- #


class UserCreationException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class InvalidPasswordException(UserCreationException):
    def __init__(self, password, message="The password contains invalid characters"):
        invalid_characters = ""
        for c in password:
            if c not in password_enabled_characters:
                invalid_characters += c
        if len(invalid_characters) > 0:
            self.message = message + ": " + invalid_characters
        else:
            self.message = message
        super().__init__(self.message)


class InvalidUsernameException(UserCreationException):
    def __init__(self, message=None):
        if message is None:
            self.message = "The username can contains only letters, numbers and " + username_additional_characters
        else:
            self.message = message
        super().__init__(self.message)


class PasswordTooLongException(UserCreationException):
    def __init__(self, password: str):
        self.message = ("The password is too long (max length: " + str(password_max_length) +
                        ", actual length: " + str(len(password)) + ")")
        super().__init__(self.message)


class UsernameTooLongException(UserCreationException):
    def __init__(self, username: str):
        self.message = ("The username is too long (max length: " + str(username_max_length) +
                        ", actual length: " + str(len(username)) + ")")
        super().__init__(self.message)


class UserExistException(UserCreationException):
    def __init__(self, username):
        self.message = "Username " + username + " already exist!"
        super().__init__(self.message)


class UserNotExistException(Exception):
    def __init__(self, username):
        self.message = "Username " + username + " does not exist!"
        super().__init__(self.message)
