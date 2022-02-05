"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        user1 = User.signup('test1', 'test1@testing.com', 'password', None)
        user1.id = 131313
        user2 = User.signup('test2', 'test2@testing.com', 'password', None)
        user2.id = 131315

        db.session.commit()

        user1 = User.query.get(131313)
        user2 = User.query.get(131315)

        self.user1 = user1
        self.user2 = user2

        self.client = app.test_client()
    
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
    
    def test_user_follows(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertEqual(len(self.user1.following), 1)
        self.assertEqual(len(self.user1.followers), 0)
        self.assertEqual(len(self.user2.following), 0)
        self.assertEqual(len(self.user2.followers), 1)
    
    def test_is_following(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user1.is_following(self.user2))
        self.assertFalse(self.user2.is_following(self.user1))

    def test_is_followed_by(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user2.is_followed_by(self.user1))
        self.assertFalse(self.user1.is_followed_by(self.user2))
    
    def test_valid_signup(self):
        user_test = User.signup('testing', 'testing@testing.com', 'password', None)
        user_test.id = 121212
        db.session.commit()

        user_test = User.query.get(121212)
        self.assertEqual(user_test.username, 'testing')
        self.assertEqual(user_test.email, 'testing@testing.com')
        self.assertNotEqual(user_test.password, 'password')
        # With Bcrypt, strings should start with $2b$
        self.assertTrue(user_test.password.startswith("$2b$"))
    
    def test_invalid_username_signup(self):
        invalid_user = User.signup(None, 'test5@email.com', 'password', None)
        invalid_user.id = 444444

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_invalid_email_signup(self):
        invalid_user = User.signup('hello', None, 'password', None)
        invalid_user.id = 555555
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup('testtest', 'testtest@test.com', None, None)
    
    def test_valid_authentication(self):
        user = User.authenticate(self.user1.username, 'password')
        self.assertIsNotNone(user)
        self.assertEqual(user.id, self.user1.id)
    
    def test_invalid_username(self):
        self.assertFalse(User.authenticate("notavaliduser", "password"))
    
    def test_invalid_password(self):
        self.assertFalse(User.authenticate(self.user1.username, 'wrongpassword'))
            

