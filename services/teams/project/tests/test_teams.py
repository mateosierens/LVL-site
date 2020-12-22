# services/teams/project/tests/test_teams.py

import json
import unittest

from project import db
from project.api.models import Team, Club
from project.tests.base import BaseTestCase

def add_club(stamNumber, name, address, zipcode, city, website):
    club = Club(stamNumber, name, address, zipcode, city, website)
    db.session.add(club)
    db.session.commit()
    return club

def add_team(stamNumber, suffix, color):
    team = Team(stamNumber, suffix, color)
    db.session.add(team)
    db.session.commit()
    return team

class TestTeamsService(BaseTestCase):
    """Test for the Teams Service."""



    ### TEAMS ###

    def test_teams(self):
        """Ensure the /ping route behaves correctly for teams."""
        response = self.client.get('/teams/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_add_team(self):
        """Ensure a new team can be added to the database"""
        add_club(13, 'WINAK', 'winakstraat 500', 2610, 'Wilrijk', 'www.winak.be')
        with self.client:
            response = self.client.post(
                '/teams',
                data=json.dumps({
                    'stamnumber': 13,
                    'suffix': None,
                    'color': 'zwart-oranje',
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('Team successfully created!', data['message'])
            self.assertIn('success', data['status'])

    def test_add_team_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty."""
        add_club(13, 'WINAK', 'winakstraat 500', 2610, 'Wilrijk', 'www.winak.be')
        with self.client:
            response = self.client.post(
                '/teams',
                data=json.dumps({}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_team_invalid_json_keys(self):
        """
        Ensure error is thrown if the JSON object does not contain all fields.
        """
        add_club(13, 'WINAK', 'winakstraat 500', 2610, 'Wilrijk', 'www.winak.be')
        with self.client:
            response = self.client.post(
                '/teams',
                data=json.dumps({'stamnumber': 13}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_team_nonexistent_stamnumber(self):
        """Ensure error is thrown if the stamnumber does not belong to a club."""
        add_club(13, 'WINAK', 'winakstraat 500', 2610, 'Wilrijk', 'www.winak.be')
        with self.client:
            response = self.client.post(
                '/teams',
                data=json.dumps({
                    'stamnumber': 3,
                    'suffix': None,
                    'color': 'zwart-oranje',
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                'No club found with that stamnumber.', data['message']
            )
            self.assertIn('fail', data['status'])

    def test_single_team(self):
        """Ensure get single team behaves correctly."""
        add_club(13, 'WINAK', 'winakstraat 500', 2610, 'Wilrijk', 'www.winak.be')
        team = add_team(13, None, 'zwart-oranje')
        with self.client:
            response = self.client.get(f'/teams/{team.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(13, data['data']['stamnumber'])
            self.assertEqual(None, data['data']['suffix'])
            self.assertIn('zwart-oranje', data['data']['color'])
            self.assertIn('success', data['status'])

    def test_single_team_no_id(self):
        """Ensure error is thrown if an id is not provided"""
        with self.client:
            response = self.client.get('/teams/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Team does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_team_incorrect_id(self):
        """Ensure error is thrown if the id does not exist."""
        with self.client:
            response = self.client.get('/teams/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Team does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_all_teams(self):
        """Ensure get all teams behaves correctly"""
        add_club(13, 'WINAK', 'winakstraat 500', 2610, 'Wilrijk', 'www.winak.be')
        add_club(14, 'test', 'teststraat 500', 1111, 'Mortsel', 'www.test.be')
        add_team(13, None, 'zwart-oranje')
        add_team(14, None, 'geel')

        with self.client:
            response = self.client.get('/teams')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['data']['teams']), 2)
            self.assertEqual(13, data['data']['teams'][0]['stamnumber'])
            self.assertEqual(None, data['data']['teams'][0]['suffix'])
            self.assertIn('zwart-oranje', data['data']['teams'][0]['color'])
            self.assertEqual(14, data['data']['teams'][1]['stamnumber'])
            self.assertEqual(None, data['data']['teams'][1]['suffix'])
            self.assertIn('geel', data['data']['teams'][1]['color'])
            self.assertIn('success', data['status'])

    def test_delete_team(self):
        """Ensure a team is deleted when invoking the delete team function"""
        add_club(13, 'WINAK', 'winakstraat 500', 2610, 'Wilrijk', 'www.winak.be')
        team = add_team(13, None, 'zwart-oranje')
        with self.client:
            response = self.client.delete(f'/teams/{team.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('success', data['status'])
            self.assertIn('Team deleted', data['message'])
            self.assertNotIn(team, Team.query.filter_by(id=int(team.id)))

    def test_delete_team_no_id(self):
        """Ensure error is thrown if an id is not provided when trying to delete team"""
        with self.client:
            response = self.client.delete('/teams/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Team does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_delete_team_incorrect_id(self):
        """Ensure error is thrown if the id does not exist when trying to delete team"""
        with self.client:
            response = self.client.delete('/teams/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Team does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_update_team(self):
        """Ensure a team can be updated in the database"""
        add_club(13, 'WINAK', 'winakstraat 500', 2610, 'Wilrijk', 'www.winak.be')
        add_club(15, 'WINAK2', 'winakstraat 500', 2610, 'Wilrijk', 'www.winak.be')
        team = add_team(13, None, 'zwart-oranje')
        with self.client:
            response = self.client.put(
                f'/teams/{team.id}',
                data=json.dumps({
                    'stamnumber': 15,
                    'suffix': None,
                    'color': 'zwart-oranje',
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('Team updated.', data['message'])
            self.assertIn('success', data['status'])

    def test_update_team_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty when trying to update team."""
        add_club(13, 'WINAK', 'winakstraat 500', 2610, 'Wilrijk', 'www.winak.be')
        add_club(15, 'WINAK2', 'winakstraat 500', 2610, 'Wilrijk', 'www.winak.be')
        team = add_team(13, None, 'zwart-oranje')
        with self.client:
            response = self.client.put(
                f'/teams/{team.id}',
                data=json.dumps({}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_update_team_nonexistent_stamnumber(self):
        """Ensure error is thrown if the club with given stamnumber does not exist."""
        add_club(13, 'WINAK', 'winakstraat 500', 2610, 'Wilrijk', 'www.winak.be')
        team = add_team(13, None, 'zwart-oranje')
        with self.client:
            response = self.client.put(
                f'/teams/{team.id}',
                data=json.dumps({
                    'stamnumber': 3,
                    'suffix': None,
                    'color': 'zwart-oranje',
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                'No club found with that stamnumber.', data['message']
            )
            self.assertIn('fail', data['status'])

    def test_update_team_no_id(self):
        """Ensure error is thrown if an id is not provided when trying to update team"""
        with self.client:
            response = self.client.put('/teams/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Team does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_update_team_incorrect_id(self):
        """Ensure error is thrown if the id does not exist when trying to update team"""
        with self.client:
            response = self.client.put('/teams/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Team does not exist', data['message'])
            self.assertIn('fail', data['status'])



    ### CLUBS ###

    def test_clubs(self):
        """Ensure the /ping route behaves correctly for clubs."""
        response = self.client.get('/clubs/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_add_club(self):
        """Ensure a new club can be added to the database"""
        with self.client:
            response = self.client.post(
                '/clubs',
                data=json.dumps({
                    'stamnumber': 13,
                    'name': 'WINAK',
                    'address': 'winakstraat 500',
                    'zipcode': 2610,
                    'city': 'Wilrijk',
                    'website': 'www.winak.be'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('Club successfully created!', data['message'])
            self.assertIn('success', data['status'])

    def test_add_club_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty."""
        with self.client:
            response = self.client.post(
                '/clubs',
                data=json.dumps({}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_club_invalid_json_keys(self):
        """
        Ensure error is thrown if the JSON object does not contain all fields.
        """
        with self.client:
            response = self.client.post(
                '/clubs',
                data=json.dumps({'stamnumber': 13}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_club(self):
        """Ensure get single club behaves correctly."""
        club = add_club(13, 'WINAK', 'winakstraat 500', 2610, 'Wilrijk', 'www.winak.be')
        with self.client:
            response = self.client.get(f'/clubs/{club.stamNumber}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(13, data['data']['stamnumber'])
            self.assertIn('WINAK', data['data']['name'])
            self.assertIn('winakstraat 500', data['data']['address'])
            self.assertEqual(2610, data['data']['zipcode'])
            self.assertIn('Wilrijk', data['data']['city'])
            self.assertIn('www.winak.be', data['data']['website'])
            self.assertIn('success', data['status'])

    def test_single_club_no_stamnumber(self):
        """Ensure error is thrown if a stamnumber is not provided"""
        with self.client:
            response = self.client.get('/clubs/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Club does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_club_incorrect_stamnumber(self):
        """Ensure error is thrown if the stamnumber does not exist."""
        with self.client:
            response = self.client.get('/clubs/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Club does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_all_clubs(self):
        """Ensure get all clubs behaves correctly"""
        add_club(13, 'WINAK', 'winakstraat 500', 2610, 'Wilrijk', 'www.winak.be')
        add_club(14, 'test', 'teststraat 500', 1111, 'Mortsel', 'www.test.be')

        with self.client:
            response = self.client.get('/clubs')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['data']['clubs']), 2)
            self.assertEqual(13, data['data']['clubs'][0]['stamnumber'])
            self.assertIn('WINAK', data['data']['clubs'][0]['name'])
            self.assertIn('winakstraat 500', data['data']['clubs'][0]['address'])
            self.assertEqual(2610, data['data']['clubs'][0]['zipcode'])
            self.assertIn('Wilrijk', data['data']['clubs'][0]['city'])
            self.assertIn('www.winak.be', data['data']['clubs'][0]['website'])
            self.assertEqual(14, data['data']['clubs'][1]['stamnumber'])
            self.assertIn('test', data['data']['clubs'][1]['name'])
            self.assertIn('teststraat 500', data['data']['clubs'][1]['address'])
            self.assertEqual(1111, data['data']['clubs'][1]['zipcode'])
            self.assertIn('Mortsel', data['data']['clubs'][1]['city'])
            self.assertIn('www.test.be', data['data']['clubs'][1]['website'])
            self.assertIn('success', data['status'])

    def test_delete_club(self):
        """Ensure a team is deleted when invoking the delete team function"""
        club = add_club(13, 'WINAK', 'winakstraat 500', 2610, 'Wilrijk', 'www.winak.be')
        with self.client:
            response = self.client.delete(f'/clubs/{club.stamNumber}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('success', data['status'])
            self.assertIn('Club deleted', data['message'])
            self.assertNotIn(club, Club.query.filter_by(stamNumber=int(club.stamNumber)))

    def test_delete_club_no_stamnumber(self):
        """Ensure error is thrown if a stamnumber is not provided when trying to delete club"""
        with self.client:
            response = self.client.delete('/clubs/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Club does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_delete_club_incorrect_stamnumber(self):
        """Ensure error is thrown if the stamnumber does not exist when trying to delete club"""
        with self.client:
            response = self.client.delete('/clubs/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Club does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_update_club(self):
        """Ensure a club can be updated in the database"""
        club = add_club(13, 'WINAK', 'winakstraat 500', 2610, 'Wilrijk', 'www.winak.be')
        with self.client:
            response = self.client.put(
                f'/clubs/{club.stamNumber}',
                data=json.dumps({
                    'stamnumber': 15,
                    'name': 'WINAK',
                    'address': 'winakstraat 500',
                    'zipcode': 2640,
                    'city': 'Wilrijk',
                    'website': 'www.winak.be'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            # self.assertEqual(response.status_code, 200)
            self.assertIn('Club updated.', data['message'])
            self.assertIn('success', data['status'])

    def test_update_club_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty when trying to update club."""
        club = add_club(13, 'WINAK', 'winakstraat 500', 2610, 'Wilrijk', 'www.winak.be')
        with self.client:
            response = self.client.put(
                f'/clubs/{club.stamNumber}',
                data=json.dumps({}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_update_club_no_stamnumber(self):
        """Ensure error is thrown if an stamnumber is not provided when trying to update club"""
        with self.client:
            response = self.client.put('/clubs/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Club does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_update_club_incorrect_stamnumber(self):
        """Ensure error is thrown if the stamnumber does not exist when trying to update club"""
        with self.client:
            response = self.client.put('/clubs/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Club does not exist', data['message'])
            self.assertIn('fail', data['status'])

if __name__ == '__main__':
    unittest.main()