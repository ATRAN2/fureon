import datetime
import hashlib
import hmac
import logging
import re

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, validates
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
    tokens = relationship("Token", backref="user")

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

class Token(Base):
    __tablename__ = 'token'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    value = Column('value', String)
    created_on = Column(DateTime)

    def __init__(self, user):
        self.user = user
        self.created_on = datetime.datetime.now()
        self.value = hmac.new(
                 config.SECRET_KEY,
                 self.user.username + str(self.created_on),
                 hashlib.sha256).hexdigest()


class UserManager(ModelManager):
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
        new_token = Token(user)
        self._session.add(new_token)
        self._session.commit()
        return new_token.value

    def validate_token(self, user, token_hex):
        self._purge_old_tokens()
        possible_tokens = user.tokens
        for token in possible_tokens:
            if hmac.compare_digest(bytes(token_hex), bytes(token.value)):
                return True
        return False

    def get_user_count(self):
        return self._session.query(User.id).count()

    def _purge_old_tokens(self):
        current_time = datetime.datetime.utcnow()
        one_week_ago = current_time - datetime.timedelta(weeks=1)
        self._session.query(Token).filter(
            Token.created_on < one_week_ago).delete()
        self._session.commit()
