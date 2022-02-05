import os
from unittest import TestCase
from models import db, User, Message, Follows, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class ViewsTestCase(TestCase):
    '''Test what the user views on web pages'''

    def setUp(self):

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup('testuser', 'testuser@test.com', 'password', None)
        self.testuser.id = 99999

        self.u1 = User.signup('user1', 'user1@test.com', 'password', None)
        self.u1.id = 11111
        self.u2 = User.signup('user2', 'user2@test.com', 'password', None)
        self.u2.id = 22222
        self.u3 = User.signup('user3', 'user3@test.com', 'password', None)
        self.u3.id = 33333
        self.u4 = User.signup('user4', 'user4@test.com', 'password', None)
        self.u4.id = 44444

        db.session.commit()
    
    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp
    
    def test_users_index(self):
        with self.client as c:
            resp = c.get('/users')

            self.assertIn('@testuser', str(resp.data))
            self.assertIn('@user1', str(resp.data))
            self.assertIn('@user2', str(resp.data))
            self.assertIn('@user3', str(resp.data))
            self.assertIn('@user4', str(resp.data))
    
    def test_search_user(self):
        with self.client as c:
            resp = c.get('/users?q=test')

            self.assertIn('@testuser', str(resp.data))

            self.assertNotIn('@user1', str(resp.data))
            self.assertNotIn('@user2', str(resp.data))
            self.assertNotIn('@user3', str(resp.data))
            self.assertNotIn('@user4', str(resp.data))
    
    def setup_likes(self):
        m1 = Message(id= 2121, text='hello', user_id=self.u1.id)
        m2 = Message(text='hello dude', user_id=self.testuser.id)
        m3 = Message(id=2222, text='hello world', user_id=self.u3.id)

        db.session.add_all([m1, m2, m3])
        db.session.commit()

        like = Likes(user_id=self.testuser.id, message_id=m1.id)

        db.session.add(like)
        db.session.commit()

    def test_user_likes(self):
        self.setup_likes()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f'/users/{self.testuser.id}/likes')
            
            self.assertIn('@user1', str(resp.data))
            self.assertNotIn('@user3', str(resp.data))
    
    def setup_followers(self):
        self.testuser.following.append(self.u1)
        self.testuser.following.append(self.u4)
        self.u3.following.append(self.testuser)

        db.session.commit()
    
    def test_followers(self):
        self.setup_followers()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get(f'/users/{self.testuser.id}/followers')
            
            self.assertNotIn('@user1', str(resp.data))
            self.assertNotIn('@user2', str(resp.data))
            self.assertIn('@user3', str(resp.data))
            self.assertNotIn('@user4', str(resp.data))

    def test_following(self):
        self.setup_followers()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get(f'/users/{self.testuser.id}/following')
            
            self.assertIn('@user1', str(resp.data))
            self.assertNotIn('@user2', str(resp.data))
            self.assertNotIn('@user3', str(resp.data))
            self.assertIn('@user4', str(resp.data))

    def test_homepage(self):
        self.setup_likes()
        self.setup_followers()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get('/')

            self.assertIn('@testuser', str(resp.data))
            self.assertIn('@user1', str(resp.data))
            self.assertNotIn('@user2', str(resp.data))
            self.assertNotIn('@user3', str(resp.data))
            self.assertNotIn('@user4', str(resp.data))



