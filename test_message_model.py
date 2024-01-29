import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        u = User.signup("testuser", "test@test.com",  "HASHED_PASSWORD", None)
        u.id = 1

        db.session.commit()

        self.u = u

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_make_message(self):
        """Tests Making Messages for users"""

        msg = Message(text='Test msg for user 1', user_id=1)
        msg.id = 1

        db.session.add(msg)
        db.session.commit()

        self.assertEqual(1, len(Message.query.all()))
        self.assertIn(msg, self.u.messages)

        msg = Message.query.get(1)
        self.assertEqual(msg.text, 'Test msg for user 1')

    def test_msg_text_err(self):
        """Tests Invalid Text Message Attempt"""

        ###
        # Tests when text is nulled
        ###
        with self.assertRaises(IntegrityError) as context:
            msg = Message(text=None, user_id=1)

            db.session.add(msg)
            db.session.commit()
            db.session.rollback();    

    def test_msg_id_err(self):
        """Tests Invalid ID Message Attempt"""
        ###
        # Tests when user_id is nulled
        ###
        with self.assertRaises(IntegrityError) as context:
            msg2 = Message(text='Should error', user_id=None)

            db.session.add(msg2)
            db.session.commit()
            db.session.rollback();

        # Test to make sure all errored and no message was made:
            
    def test_message_user_relationship(self):
        """Tests link between user and message"""
        msg = Message(text='Test msg for user 1', user_id=1)
        msg.id = 1

        db.session.add(msg)
        db.session.commit()

        self.assertIn(msg, self.u.messages)
        self.assertEqual(msg.text, self.u.messages[0].text)

