# services/matches/project/tests/test_matches.py

import json
import unittest

from project import db
from project.api.models import Referee, Division, Status, Match
from project.tests.base import BaseTestCase


def add_referee(first_name, last_name, address, zip_code, city, phone_number, email, date_of_birth):
    referee = Referee(first_name, last_name, address, zip_code, city, phone_number, email, date_of_birth)
    db.session.add(referee)
    db.session.commit()
    return referee

def add_division(division_name):
    division = Division(division_name)
    db.session.add(division)
    db.session.commit()
    return division

def add_status(status_name):
    status = Status(status_name)
    db.session.add(status)
    db.session.commit()
    return status

class TestMatchesService(BaseTestCase):
    """Test for the Matches Service."""

    ### referees ###
    # test ping
    def test_referees(self):
        """Ensure the /ping route behaves correctly for referees."""
        response = self.client.get('/referees/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    # test create referee
    def test_add_referee(self):
        """Ensure a new referee can be added to the database"""
        with self.client:
            response = self.client.post(
                '/referees',
                data=json.dumps({
                    'firstname': "Jan",
                    'lastname': "Peeters",
                    'address': "Lentestraat 5",
                    'zipcode': 2000,
                    'city': "Antwerpen",
                    'phonenumber': "024771211",
                    'email': "jan.peeters@l-v-l.be",
                    'birthdate': "1969-06-09"
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('Referee successfully created!', data['message'])
            self.assertIn('success', data['status'])

    # test create referee with wrong json
    def test_add_referee_invalid_json_keys(self):
        """
        Ensure error is thrown if the JSON object does not contain all fields.
        """
        with self.client:
            response = self.client.post(
                '/referees',
                data=json.dumps({'zipcode': 2000}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    # test get referee
    def test_single_referee(self):
        """Ensure get single referee behaves correctly."""
        referee = add_referee("Jan", "Peeters", "Lentestraat 5", 2000, "Antwerpen", "024771211", "jan.peeters@l-v-l.be",
                              "1969-06-09")
        with self.client:
            response = self.client.get(f'/referees/{referee.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn("Jan", data['data']['firstname'])
            self.assertIn("Peeters", data['data']['lastname'])
            self.assertIn('Lentestraat 5', data['data']['address'])
            self.assertEqual(2000, data['data']['zipcode'])
            self.assertIn('Antwerpen', data['data']['city'])
            self.assertIn('024771211', data['data']['phonenumber'])
            self.assertIn('jan.peeters@l-v-l.be', data['data']['email'])
            self.assertIn('1969-06-09', data['data']['birthdate'])
            self.assertIn('success', data['status'])

    # test get referee wrong id
    def test_single_referee_incorrect_id(self):
        """Ensure error is thrown if the id does not exist."""
        with self.client:
            response = self.client.get('/referees/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Referee does not exist', data['message'])
            self.assertIn('fail', data['status'])

    # test get referee no id
    def test_single_referee_no_id(self):
        """Ensure error is thrown if an id is not provided"""
        with self.client:
            response = self.client.get('/referees/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Referee does not exist', data['message'])
            self.assertIn('fail', data['status'])

    # test get all referees
    def test_all_referees(self):
        """Ensure get all referees behaves correctly"""
        add_referee("Jan", "Peeters", "Lentestraat 5", 2000, "Antwerpen", "024771211", "jan.peeters@l-v-l.be",
                              "1969-06-09")
        add_referee("Simon", "Peeters", "Lentestraat 5", 2000, "Antwerpen", "024771211", "jan.peeters@l-v-l.be",
                              "1969-06-09")

        with self.client:
            response = self.client.get('/referees')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['data']['referees']), 2)
            self.assertIn("Jan", data['data']['referees'][0]['firstname'])
            self.assertIn("Peeters", data['data']['referees'][0]['lastname'])
            self.assertIn('Lentestraat 5', data['data']['referees'][0]['address'])
            self.assertEqual(2000, data['data']['referees'][0]['zipcode'])
            self.assertIn('Antwerpen', data['data']['referees'][0]['city'])
            self.assertIn('024771211', data['data']['referees'][0]['phonenumber'])
            self.assertIn('jan.peeters@l-v-l.be', data['data']['referees'][0]['email'])
            self.assertIn('1969-06-09', data['data']['referees'][0]['birthdate'])
            self.assertIn("Simon", data['data']['referees'][1]['firstname'])
            self.assertIn("Peeters", data['data']['referees'][1]['lastname'])
            self.assertIn('Lentestraat 5', data['data']['referees'][1]['address'])
            self.assertEqual(2000, data['data']['referees'][1]['zipcode'])
            self.assertIn('Antwerpen', data['data']['referees'][1]['city'])
            self.assertIn('024771211', data['data']['referees'][1]['phonenumber'])
            self.assertIn('jan.peeters@l-v-l.be', data['data']['referees'][1]['email'])
            self.assertIn('1969-06-09', data['data']['referees'][1]['birthdate'])
            self.assertIn('success', data['status'])

    # test update referee
    def test_update_referee(self):
        """Ensure a referee can be updated in the database"""
        referee = add_referee("Jan", "Peeters", "Lentestraat 5", 2000, "Antwerpen", "024771211", "jan.peeters@l-v-l.be",
                              "1969-06-09")
        with self.client:
            response = self.client.put(
                f'/referees/{referee.id}',
                data=json.dumps({
                    'firstname': "Jan",
                    'lastname': "Peeters",
                    'address': "Lentestraat 5",
                    'zipcode': 2000,
                    'city': "Antwerpen",
                    'phonenumber': "024771211",
                    'email': "jan.peeters@l-v-l.be",
                    'birthdate': "1969-06-09"
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('Referee updated.', data['message'])
            self.assertIn('success', data['status'])

    # test update referee invalid json
    def test_update_referee_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty when trying to update referee."""
        referee = add_referee("Jan", "Peeters", "Lentestraat 5", 2000, "Antwerpen", "024771211", "jan.peeters@l-v-l.be",
                              "1969-06-09")
        with self.client:
            response = self.client.put(
                f'/referees/{referee.id}',
                data=json.dumps({}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    # test update referee wrong id
    def test_update_referee_incorrect_id(self):
        """Ensure error is thrown if the id does not exist when trying to update referee"""
        with self.client:
            response = self.client.put('/referees/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Referee does not exist', data['message'])
            self.assertIn('fail', data['status'])

    # test update referee no id
    def test_update_referee_no_id(self):
        """Ensure error is thrown if an id is not provided when trying to update referee"""
        with self.client:
            response = self.client.put('/referees/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Referee does not exist', data['message'])
            self.assertIn('fail', data['status'])

    # test delete referee
    def test_delete_referee(self):
        """Ensure a referee is deleted when invoking the delete referee function"""
        referee = add_referee("Jan", "Peeters", "Lentestraat 5", 2000, "Antwerpen", "024771211", "jan.peeters@l-v-l.be",
                    "1969-06-09")
        with self.client:
            response = self.client.delete(f'/referees/{referee.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('success', data['status'])
            self.assertIn('Referee deleted', data['message'])
            self.assertNotIn(referee, Referee.query.filter_by(id=int(referee.id)))

    # test delete referee with wrong id
    def test_delete_referee_incorrect_id(self):
        """Ensure error is thrown if the id does not exist when trying to delete referee"""
        with self.client:
            response = self.client.delete('/referees/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Referee does not exist', data['message'])
            self.assertIn('fail', data['status'])

    # test delete referee no id
    def test_delete_referee_no_id(self):
        """Ensure error is thrown if an id is not provided when trying to delete referee"""
        with self.client:
            response = self.client.delete('/referees/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Referee does not exist', data['message'])
            self.assertIn('fail', data['status'])


    ### Division ###
    def test_division(self):
        """Ensure the /ping route behaves correctly for divisions."""
        response = self.client.get('/divisions/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    # test create division
    def test_add_division(self):
        """Ensure a new division can be added to the database"""
        with self.client:
            response = self.client.post(
                '/divisions',
                data=json.dumps({
                    'divisionname': '1ste Afdeling'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('Division successfully created!', data['message'])
            self.assertIn('success', data['status'])

    # test create division with wrong json
    def test_add_division_invalid_json_keys(self):
        """
        Ensure error is thrown if the JSON object does not contain all fields.
        """
        with self.client:
            response = self.client.post(
                '/divisions',
                data=json.dumps({}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    # test get division
    def test_single_division(self):
        """Ensure get single division behaves correctly."""
        division = add_division('1ste Afdeling')
        with self.client:
            response = self.client.get(f'/divisions/{division.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn("1ste Afdeling", data['data']['divisionname'])
            self.assertIn('success', data['status'])

    # test get division wrong id
    def test_single_division_incorrect_id(self):
        """Ensure error is thrown if the id does not exist."""
        with self.client:
            response = self.client.get('/divisions/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Division does not exist', data['message'])
            self.assertIn('fail', data['status'])

    # test get referee no id
    def test_single_division_no_id(self):
        """Ensure error is thrown if an id is not provided"""
        with self.client:
            response = self.client.get('/divisions/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Division does not exist', data['message'])
            self.assertIn('fail', data['status'])

    # test get all referees
    def test_all_divisions(self):
        """Ensure get all divisions behaves correctly"""
        add_division('1ste Afdeling')
        add_division('2de Afdeling')
        with self.client:
            response = self.client.get('/divisions')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['data']['divisions']), 2)
            self.assertIn("1ste Afdeling", data['data']['divisions'][0]['divisionname'])
            self.assertIn('2de Afdeling', data['data']['divisions'][1]['divisionname'])
            self.assertIn('success', data['status'])

    # test update divisions
    def test_update_divisions(self):
        """Ensure a division can be updated in the database"""
        division = add_division('1ste Afdelng')
        with self.client:
            response = self.client.put(
                f'/divisions/{division.id}',
                data=json.dumps({
                    'divisionname': '1ste Afdeling'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('Division updated.', data['message'])
            self.assertIn('success', data['status'])

    # test update division invalid json
    def test_update_division_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty when trying to update division."""
        division = add_division('1ste Afdeling')
        with self.client:
            response = self.client.put(
                f'/divisions/{division.id}',
                data=json.dumps({}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    # test update division wrong id
    def test_update_division_incorrect_id(self):
        """Ensure error is thrown if the id does not exist when trying to update division"""
        with self.client:
            response = self.client.put('/divisions/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Division does not exist', data['message'])
            self.assertIn('fail', data['status'])

    # test update division no id
    def test_update_division_no_id(self):
        """Ensure error is thrown if an id is not provided when trying to update division"""
        with self.client:
            response = self.client.put('/divisions/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Division does not exist', data['message'])
            self.assertIn('fail', data['status'])

    # test delete referee
    def test_delete_division(self):
        """Ensure a division is deleted when invoking the delete division function"""
        division = add_division('1ste Afdelng')
        with self.client:
            response = self.client.delete(f'/divisions/{division.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('success', data['status'])
            self.assertIn('Division deleted', data['message'])
            self.assertNotIn(division, Division.query.filter_by(id=int(division.id)))

    # test delete division with wrong id
    def test_delete_division_incorrect_id(self):
        """Ensure error is thrown if the id does not exist when trying to delete division"""
        with self.client:
            response = self.client.delete('/divisions/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Division does not exist', data['message'])
            self.assertIn('fail', data['status'])

    # test delete division no id
    def test_delete_division_no_id(self):
        """Ensure error is thrown if an id is not provided when trying to delete division"""
        with self.client:
            response = self.client.delete('/divisions/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Division does not exist', data['message'])
            self.assertIn('fail', data['status'])


    ### Status ###
    def test_status(self):
        """Ensure the /ping route behaves correctly for status."""
        response = self.client.get('/status/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    # test create status
    def test_add_status(self):
        """Ensure a new status can be added to the database"""
        with self.client:
            response = self.client.post(
                '/status',
                data=json.dumps({
                    'statusname': 'Uitstel'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('Status successfully created!', data['message'])
            self.assertIn('success', data['status'])

    # test create status with wrong json
    def test_add_status_invalid_json_keys(self):
        """
        Ensure error is thrown if the JSON object does not contain all fields.
        """
        with self.client:
            response = self.client.post(
                '/status',
                data=json.dumps({}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    # test get status
    def test_single_status(self):
        """Ensure get single status behaves correctly."""
        status = add_status('Uitstel')
        with self.client:
            response = self.client.get(f'/status/{status.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn("Uitstel", data['data']['statusname'])
            self.assertIn('success', data['status'])

    # test get status wrong id
    def test_single_status_incorrect_id(self):
        """Ensure error is thrown if the id does not exist."""
        with self.client:
            response = self.client.get('/status/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Status does not exist', data['message'])
            self.assertIn('fail', data['status'])

    # test get status no id
    def test_single_status_no_id(self):
        """Ensure error is thrown if an id is not provided"""
        with self.client:
            response = self.client.get('/status/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Status does not exist', data['message'])
            self.assertIn('fail', data['status'])

    # test get all status
    def test_all_status(self):
        """Ensure get all status behaves correctly"""
        add_status('test1')
        add_status('test2')
        with self.client:
            response = self.client.get('/status')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['data']['status']), 2)
            self.assertIn('test1', data['data']['status'][0]['statusname'])
            self.assertIn('test2', data['data']['status'][1]['statusname'])
            self.assertIn('success', data['status'])

    # test update status
    def test_update_status(self):
        """Ensure a status can be updated in the database"""
        status = add_status('Uitstl')
        with self.client:
            response = self.client.put(
                f'/status/{status.id}',
                data=json.dumps({
                    'statusname': 'Uitstel'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('Status updated.', data['message'])
            self.assertIn('success', data['status'])

    # test update status invalid json
    def test_update_status_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty when trying to update status."""
        status = add_status('Uitstel')
        with self.client:
            response = self.client.put(
                f'/status/{status.id}',
                data=json.dumps({}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    # test update status wrong id
    def test_update_status_incorrect_id(self):
        """Ensure error is thrown if the id does not exist when trying to update status"""
        with self.client:
            response = self.client.put('/status/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Status does not exist', data['message'])
            self.assertIn('fail', data['status'])

    # test update status no id
    def test_update_status_no_id(self):
        """Ensure error is thrown if an id is not provided when trying to update status"""
        with self.client:
            response = self.client.put('/status/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Status does not exist', data['message'])
            self.assertIn('fail', data['status'])

    # test delete status
    def test_delete_status(self):
        """Ensure a division is deleted when invoking the delete status function"""
        status = add_status('Uitstel')
        with self.client:
            response = self.client.delete(f'/status/{status.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('success', data['status'])
            self.assertIn('Status deleted', data['message'])
            self.assertNotIn(status, Status.query.filter_by(id=int(status.id)))

    # test delete status with wrong id
    def test_delete_status_incorrect_id(self):
        """Ensure error is thrown if the id does not exist when trying to delete status"""
        with self.client:
            response = self.client.delete('/status/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Status does not exist', data['message'])
            self.assertIn('fail', data['status'])

    # test delete status no id
    def test_delete_status_no_id(self):
        """Ensure error is thrown if an id is not provided when trying to delete status"""
        with self.client:
            response = self.client.delete('/status/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Status does not exist', data['message'])
            self.assertIn('fail', data['status'])

if __name__ == '__main__':
    unittest.main()
