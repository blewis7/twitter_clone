# run these tests with:
#
#    python -m unittest test_message_model.py

import os
from unittest import TestCase
from models import db, User, Message, Likes, Follows

# create database in venv:
#
#   createdb warbler-test
#
# Do this step first before running tests!

os.environ['DATABASE_URL'] = 'postgresql:///warbler-test'

from app import app

db.create_all()

class UserModelTestCase(TestCase):
    def setUp(self):
        db.drop_all()
        db.create_all()

        self.user_id = 99888
        user = User.signup('test', 'testing@test.com', 'testpw', None)
        user.id = self.user_id
        db.session.commit()

        self.user = User.query.get(self.user_id)

        self.client = app.test_client()
    
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):

        message = Message(text='hello world', user_id=self.user_id)

        db.session.add(message)
        db.session.commit()

        self.assertEqual(len(self.user.messages), 1)
        self.assertEqual(self.user.messages[0].text, 'hello world')

    def test_message_likes(self):
        m1 = Message(text='testing', user_id = self.user_id)
        m2 = Message(text='testing2', user_id=self.user_id)

        u2 = User.signup('testingagain', 'test@testing.com', 'password', None)
        user_id = 777777
        u2.id = user_id
        db.session.add_all([m1, m2, u2])
        
        db.session.commit()

        u2.likes.append(m1)

        db.session.commit()

        likes = Likes.query.filter(Likes.user_id == u2.id).all()
        self.assertEqual(len(likes), 1)
        self.assertEqual(likes[0].message_id, m1.id)


