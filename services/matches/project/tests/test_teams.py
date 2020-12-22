# services/matches/project/tests/test_teams.py

import json
import unittest

from project import db
from project.api.models import Referee, Division, Status, Match
from project.tests.base import BaseTestCase

# def add_club(stamNumber, name, address, zipcode, city, website):
#     club = Club(stamNumber, name, address, zipcode, city, website)
#     db.session.add(club)
#     db.session.commit()
#     return club
#
# def add_team(stamNumber, suffix, color):
#     team = Team(stamNumber, suffix, color)
#     db.session.add(team)
#     db.session.commit()
#     return team

class TestMatchesService(BaseTestCase):
    """Test for the Matches Service."""
    pass

if __name__ == '__main__':
    unittest.main()