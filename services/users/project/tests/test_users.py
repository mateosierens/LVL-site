# services/users/project/tests/test_users.py

import json
import unittest

from project import db
from project.api.models import User
from project.tests.base import BaseTestCase

def add_user(username, password, email, club, admin):
    user = User(username=username, password=password, email=email, club=club, admin=admin)
    db.session.add(user)
    db.session.commit()
    return user

class TestUserService(BaseTestCase):
    """Test for the Users Service."""

    def test_add_user(self):
        """Ensure a new user can be added to the database"""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'michael',
                    'password': 'herman',
                    'email': 'michael@mherman.org',
                    'club': None,
                    'admin': False
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('michael@mherman.org was added!', data['message'])
            self.assertIn('success', data['status'])

    def test_add_user_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty."""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_invalid_json_keys(self):
        """
        Ensure error is thrown if the JSON object does not have a username and password key.
        """
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({'email': 'michael@mherman.org'}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_duplicate_email(self):
        """Ensure error is thrown if the email already exists."""
        with self.client:
            self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'michael',
                    'password': 'test123',
                    'email': 'michael@mherman.org',
                    'club': None,
                    'admin': False
                }),
                content_type='application/json',
            )
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'michael',
                    'password': 'test155',
                    'email': 'michael@mherman.org',
                    'club': None,
                    'admin': False
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                'Sorry. That email already exists.', data['message']
            )
            self.assertIn('fail', data['status'])

    def test_single_user(self):
        """Ensure get single user behaves correctly."""
        user = add_user('michael', 'strongpassword', 'michael@mherman.org', None, False)
        db.session.add(user)
        db.session.commit()
        with self.client:
            response = self.client.get(f'/users/{user.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('michael', data['data']['username'])
            self.assertIn('strongpassword', data['data']['password'])
            self.assertIn('michael@mherman.org', data['data']['email'])
            self.assertEqual(None, data['data']['club'])
            self.assertEqual(False, data['data']['admin'])
            self.assertIn('succes', data['status'])

    def test_single_user_no_id(self):
        """Ensure error is thrown if an id is not provided"""
        with self.client:
            response = self.client.get('/users/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user_incorrect_id(self):
        """Ensure error is thrown if the id does not exist."""
        with self.client:
            response = self.client.get('/users/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_all_users(self):
        """Ensure get all users behaves correctly"""
        add_user('michael', 'testpass1', 'michael@mherman.org', None, False)
        add_user('fletcher', 'testpass2', 'fletcher@notreal.com', None, False)
        with self.client:
            response = self.client.get('/users')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['data']['users']), 2)
            self.assertIn('michael', data['data']['users'][0]['username'])
            self.assertIn('testpass1', data['data']['users'][0]['password'])
            self.assertIn('michael@mherman.org', data['data']['users'][0]['email'])
            self.assertEqual(None, data['data']['users'][0]['club'])
            self.assertEqual(False, data['data']['users'][0]['admin'])
            self.assertIn('fletcher', data['data']['users'][1]['username'])
            self.assertIn('testpass2', data['data']['users'][1]['password'])
            self.assertIn('fletcher@notreal.com', data['data']['users'][1]['email'])
            self.assertEqual(None, data['data']['users'][1]['club'])
            self.assertEqual(False, data['data']['users'][1]['admin'])
            self.assertIn('success', data['status'])

    def test_delete_user(self):
        """Ensure a user is deleted when invoking the delete user function"""
        user = add_user('michael', 'strongpassword', 'michael@mherman.org', None, False)
        db.session.add(user)
        db.session.commit()
        with self.client:
            response = self.client.delete(f'/users/{user.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('succes', data['status'])
            self.assertIn('User deleted', data['message'])
            self.assertNotIn(user, User.query.filter_by(id=int(user.id)))

    def test_delete_user_no_id(self):
        """Ensure error is thrown if an id is not provided when trying to delete user"""
        with self.client:
            response = self.client.delete('/users/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_delete_user_incorrect_id(self):
        """Ensure error is thrown if the id does not exist when trying to delete user"""
        with self.client:
            response = self.client.delete('/users/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_update_user(self):
        """Ensure a user can be updated in the database"""
        user = add_user('michael', 'strongpassword', 'michael@mherman.org', None, False)
        db.session.add(user)
        db.session.commit()
        with self.client:
            response = self.client.put(
                f'/users/{user.id}',
                data=json.dumps({
                    'username': 'michael',
                    'password': 'herman',
                    'email': 'michael@mherman.com',
                    'club': None,
                    'admin': False
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            # self.assertEqual(response.status_code, 200)
            self.assertIn('User updated', data['message'])
            self.assertIn('success', data['status'])

    def test_update_user_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty when trying to update user."""
        user = add_user('michael', 'strongpassword', 'michael@mherman.org', None, False)
        db.session.add(user)
        db.session.commit()
        with self.client:
            response = self.client.put(
                f'/users/{user.id}',
                data=json.dumps({}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_update_user_duplicate_email(self):
        """Ensure error is thrown if the email already exists."""
        user = add_user('michael', 'strongpassword', 'michael@mherman.org', None, False)
        db.session.add(user)
        db.session.commit()
        with self.client:
            self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'michael',
                    'password': 'test123',
                    'email': 'michael@mherman.org',
                    'club': None,
                    'admin': False
                }),
                content_type='application/json',
            )
            response = self.client.put(
                f'/users/{user.id}',
                data=json.dumps({
                    'username': 'michael',
                    'password': 'test155',
                    'email': 'michael@mherman.org',
                    'club': None,
                    'admin': False
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                'Sorry. That email already exists.', data['message']
            )
            self.assertIn('fail', data['status'])

    def test_update_user_no_id(self):
        """Ensure error is thrown if an id is not provided when trying to update user"""
        with self.client:
            response = self.client.put('/users/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_update_user_incorrect_id(self):
        """Ensure error is thrown if the id does not exist when trying to update user"""
        with self.client:
            response = self.client.put('/users/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertIn('fail', data['status'])

if __name__ == '__main__':
    unittest.main()