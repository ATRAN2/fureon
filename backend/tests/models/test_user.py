from hashlib import sha256

import mock
import pytest

from fureon import db_operations
from fureon.config import SECRET_TOKEN
from fureon.exceptions import InvalidUsernameError, InvalidEmailError, \
                              DuplicateUsernameError, DuplicateEmailError
from fureon.models import user, token
from tests import testing_utils


class TestUserModel(object):
    @classmethod
    def setup_class(cls):
        pass

    def setup_method(self, method):
        testing_utils.connect_to_temporary_test_db()
        with db_operations.session_scope() as session:
            self.user_manager = user.UserManager(session)
            self.session = session
            test_user = user.User('test_username', 'test_password',
                                  'test_email@example.com')
            session.add(test_user)
            session.commit()

    def teardown_method(self, method):
        del self.user_manager

    def test_user_count(self):
        assert 1 == self.user_manager.get_user_count()
        test_users = [user.User('test_user'+i, 'p') for i in range(100)]
        self.session.add_all(test_users)
        self.session.commit()
        assert 101 == self.user_manager.get_user_count()

    def test_register_user(self):
        assert 1 == self.user_manager.get_user_count()

        self.user_manager.register_user("other_username", "other_password",
                                        "other_email@email.com")
        assert 2 == self.user_manager.get_user_count()
        new_user = self.user_manager.find_by_username("other_username").first()
        assert new_user.email == "other_email@email.com"

        self.user_manager.register_user("third_username", "third_password",
                                        "third_email@third.com")
        assert 3 == self.user_manager.get_user_count()

    def test_register_user_without_email(self):
        assert 1 == self.user_manager.get_user_count()

        self.user_manager.register_user("other_username", "other_password")
        assert 2 == self.user_manager.get_user_count(), \
                    "Failed to register user without a email"

        new_user = self.user_manager.find_by_username("other_username").first()

        assert new_user.email is None

    def test_register_user_username_validation(self):
        assert 1 == self.user_manager.get_user_count()

        with pytest.raises(InvalidUsernameError):
            self.user_manager.register_user("bad username", "other_password")

        with pytest.raises(InvalidUsernameError):
            self.user_manager.register_user("!@$%#^username", "other_password")

        with pytest.raises(InvalidUsernameError):
            self.user_manager.register_user("", "other_password")

        assert 1 == self.user_manager.get_user_count()

    def test_register_user_email_validation(self):
        assert 1 == self.user_manager.get_user_count()

        with pytest.raises(InvalidEmailError):
            self.user_manager.register_user("user", "pass", "@bad_email.org")

        with pytest.raises(InvalidEmailError):
            self.user_manager.register_user("user", "pass", "bad@")

        with pytest.raises(InvalidEmailError):
            self.user_manager.register_user("user", "pass", " ")

        with pytest.raises(InvalidEmailError):
            self.user_manager.register_user("user", "pass", "$%^%@&@&^#.**")

        assert 1 == self.user_manager.get_user_count()

    def test_register_user_duplicate_username(self):
        assert 1 == self.user_manager.get_user_count()
        self.user_manager.register_user("other_username", "other_password",
                                        "other_email@email.com")
        assert 2 == self.user_manager.get_user_count()

        with pytest.raises(DuplicateUsernameError):
            self.user_manager.register_user("other_username", "password_other",
                                            "email_other@email.com")
        assert 2 == self.user_manager.get_user_count()

    def test_register_user_duplicate_email(self):
        assert 1 == self.user_manager.get_user_count()
        self.user_manager.register_user("username1", "other_password",
                                        "other_email@email.com")
        assert 2 == self.user_manager.get_user_count()

        with pytest.raises(DuplicateEmailError):
            self.user_manager.register_user("username2", "password_other",
                                            "other_email@email.com")
        assert 2 == self.user_manager.get_user_count()

    @mock.patch('fureon.models.user.hmac.new')
    def test_generate_token(self, hmac_new):
        test_user = user.User.query.first()

        self.user_manager.generate_token(test_user)
        test_user_token = token.Token.query.first()
        
        assert test_user.tokens[0] == test_user_token

        hmac_new.assert_called_once_with(SECRET_TOKEN,
                                         test_user.username +
                                         test_user_token.datetime_added +
                                         sha256(SECRET_TOKEN).digest(),
                                         sha256)

