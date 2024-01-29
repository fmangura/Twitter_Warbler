"""Message View tests."""

import os
from unittest import TestCase
from flask import session
from models import db, connect_db, Message, User

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        u = User.signup("testuser", "test@test.com",  "HASHED_PASSWORD", None)
        u.id = 1

        u2 = User(email="user2@user.com",
                 username='testuser2',
                 password="HASHED_PASSWORD")
        u2.id = 2

        db.session.add(u2)
        db.session.commit()

        self.u = u
        self.u2 = u2

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_msg_invalid(self):
         with app.test_client() as client:
            """Tests message INVALID INPUT"""

            post_resp = client.post('/login', data={'username':'testuser', 'password':'HASHED_PASSWORD'})

            self.assertEqual(self.u.id, session[CURR_USER_KEY])

            ###
            # Test being able to create new message and redirect
            ### 
            resp = client.post('/messages/new', data={'text':None})
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn(resp.data, Message.query.all())

    def test_login_capabilities(self):
        with app.test_client() as client:
            """Tests functions of logged in users"""

            post_resp = client.post('/login', data={'username':'testuser', 'password':'HASHED_PASSWORD'})

            self.assertEqual(self.u.id, session[CURR_USER_KEY])

            ###
            # Test being able to create new message and redirect
            ### 
            resp = client.post('/messages/new', data={'text':'TEST_MESSAGE'})
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'http://localhost/users/{self.u.id}')

            ###
            # Checks if message was successfuly made
            ###
            new_msg = Message.query.filter_by(user_id=self.u.id).first()
            msg_resp = client.get(f'/users/{self.u.id}')
            html = msg_resp.get_data(as_text=True)

            self.assertIn('<p>TEST_MESSAGE</p>', html)

            ###
            # Test deleting messages
            ###
            resp = client.post(f'/messages/{new_msg.id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('<p>TEST_MESSAGE</p>', html)
            self.assertEqual(0, len(self.u.messages))

    def test_logged_out_restrictions(self):
        with app.test_client() as client:
            """Test logged out restrictions"""

            ###
            # Cannot make messages when logged out
            ###
            resp = client.post('/messages/new', data={'text':'TEST_MESSAGE'}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))
            self.assertEqual(0, len(Message.query.all()))

            ###
            # Cannot delete messages when logged out
            ###
            msg = Message(text='TESTING', user_id=2)
            msg.id = 300
            db.session.add(msg)
            db.session.commit()

            follow = client.post('/messages/300/delete', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))
            self.assertNotEqual(Message.query.filter_by(id=300), None)

