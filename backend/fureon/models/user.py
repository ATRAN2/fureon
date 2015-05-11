import logging
import re
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import validates
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy_utils import PasswordType

from fureon import config
from fureon.exceptions import (InvalidUsernameError, InvalidEmailError,
                              DuplicateUsernameError, DuplicateEmailError)
from fureon.models.base import Base, ModelManager


module_logger = logging.getLogger(__name__)

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column('username', String, unique=True)
    password = Column(PasswordType(schemes=['pbkdf2_sha512']))
    email = Column('email', String, nullable=True)

    def __init__(self, username, password, email=None):
        self.username = username
        self.password = password
        self.email = email

    @validates('username')
    def validate_username(self, key, username):
        if re.match(r"^[A-Za-z0-9_]+$", username) is None:
            raise InvalidUsernameError
        return username

    @validates('email')
    def validate_email(self, key, email):
        if email and re.match(r"[^@]+@[^@]+\.[^@]+", email) is None:
            raise InvalidEmailError
        return email


class UserManager(ModelManager):
    _serializer = URLSafeTimedSerializer(config.SECRET_KEY)

    def register_user(self, username, password, email=None):
        if self.find_by_username(username):
            raise DuplicateUsernameError
        if self.find_by_email(email):
            raise DuplicateEmailError
        new_user = User(username, password, email)
        self._session.add(new_user)
        self._session.commit()
        return new_user

    def auth_user(self, username, password):
        user = self.find_by_username(username)
        return user is not None and user.password == password
    
    def find_by_username(self, username):
        try:
            return self._session.query(User).filter_by(username=username).one()
        except NoResultFound:
            return None

    def find_by_email(self, email):
        if email is None:
            return None
        try:
            return self._session.query(User).filter_by(email=email).one()
        except NoResultFound:
            return None

    def generate_token(self, user):
        return self._serializer.dumps(user.id)

    def validate_token(self, token):
        try:
            user_id = self._serializer.loads(token)
        except (SignatureExpired, BadSignature):
            return None
        return self._session.query(User).get(user_id)

    def get_user_count(self):
        return self._session.query(User.id).count()
