import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows
from flask import session

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserModelTestCaseViews(TestCase):

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

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
    

    def test_successful_login(self):
        with app.test_client() as client:
            """Tests getting login"""
            ###
            # Tests GET login form
            ###
            resp = client.get('/login')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h2 class="join-message">Welcome back.</h2>', html)

            ###
            # Tests POST login form
            ###

            post_resp = client.post('/login', data={'username':'testuser', 'password':'HASHED_PASSWORD'})
            post_html = post_resp.get_data(as_text=True)

            self.assertEqual(post_resp.status_code, 302)
            self.assertEqual(self.u.id, session[CURR_USER_KEY])
            self.assertEqual(post_resp.location, 'http://localhost/')

    def test_login_capabilities(self):
        with app.test_client() as client:
            """Tests functions of logged in users"""

            post_resp = client.post('/login', data={'username':'testuser', 'password':'HASHED_PASSWORD'})

            self.assertEqual(self.u.id, session[CURR_USER_KEY])

            ###
            # Tests Follow
            ###
            follow = client.post('/users/follow/2')
            self.assertEqual(follow.status_code, 302)
            self.assertEqual(follow.location, f"http://localhost/users/{self.u.id}/following")
            self.assertIn(self.u, self.u2.followers)

            ###
            # Tests unFollow
            ###
            unfollow = client.post('/users/stop-following/2')
            self.assertEqual(unfollow.status_code, 302)
            self.assertEqual(unfollow.location, f"http://localhost/users/{self.u.id}/following")
            self.assertNotIn(self.u, self.u2.followers)

    def test_logged_out_restrictions(self):
        with app.test_client() as client:
            """Test logged out restrictions"""
            ###
            # Cannot Follow when logged out
            ###
            follow = client.post('/users/follow/2', follow_redirects=True)

            self.assertEqual(follow.status_code, 200)
            self.assertIn("Access unauthorized", str(follow.data))
            self.assertEqual(0, len(self.u2.followers))


