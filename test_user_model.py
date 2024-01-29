"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
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

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        u = User.signup("testuser", "test@test.com",  "HASHED_PASSWORD", None)
        u.id = 1

        u2 = User(email="user2@user.com",
                 username='testuser2',
                 password="HASHED_PASSWORD")

        db.session.add(u2)
        db.session.commit()

        self.u = u
        self.u2 = u2

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_user_model(self):
        """Does basic model work?"""

        # User should have no messages & no followers
        # self.assertEqual(len(self.u.messages), 0)
        self.assertEqual(len(self.u.followers), 0)
        self.assertEqual(2, len(User.query.all()))

        self.assertIn(User.__repr__(self.u), f'<User #{self.u.id}: {self.u.username}, {self.u.email}>')

    def test_following(self):
        """Does Following Work?"""
        self.u.following.append(self.u2)
        db.session.commit()

        """Test is_following"""
        self.assertEqual(len(self.u.following), 1)
        self.assertIn(self.u2, self.u.following)

        """Test is_followed_by"""
        self.assertEqual(len(self.u2.followers), 1)
        self.assertIn(self.u, self.u2.followers)

        """Test no_longer_following"""
        self.u.following.remove(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u2.followers), 0)
        self.assertNotIn(self.u2, self.u.following)

    def test_create_user(self):
        """Tests creating new user"""

        user = User.signup('newUser', 'newUser@user', 'password', None )
        user.id = 999
        db.session.commit()

        self.assertEqual(user.id, 999)

    def test_create_user_FAIL(self):
        """Does violating validators when creating user lead to error?"""
        
        user = User.signup(None, 'test@user', 'password', None )
        with self.assertRaises(IntegrityError) as context:
            db.session.commit()

    def test_create_user_Email_FAIL(self):
        """Does violating validators when creating user lead to error?"""

        user = User.signup('TESTESTSET', None , 'password', None )
        with self.assertRaises(IntegrityError) as context:
            db.session.commit()

    def test_create_user_Password_FAIL(self):
        """Does violating validators when creating user lead to error?"""
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", None, None)

    def test_user_authorization(self):
        """Tests authorization results """

        user = User.authenticate("testuser", "HASHED_PASSWORD")

        self.assertAlmostEqual(user.id, self.u.id)

    def test_wrong_password(self):
        """Tests getitng the wrong password"""

        user = User.authenticate("testuser", "Wrong_password")

        self.assertAlmostEqual(user, False)

    def test_wrong_username(self):
        """Tests getitng the wrong username"""

        user = User.authenticate("wonrguser", "HASHED_PASSWORD")

        self.assertAlmostEqual(user, False)


    

        
    

        