# services/users/manage.py

import unittest
import csv

from flask.cli import FlaskGroup

from project import create_app, db
from project.api.models import Referee, Division, Status, Match

app = create_app()
cli = FlaskGroup(create_app=create_app)


@cli.command()
def recreate_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command()
def test():
    """ Runs the tests without code coverage"""
    tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@cli.command()
def seed_db():
    """Seeds the database."""

    # get files
    divisions = "./data/divisions.csv"
    matches1 = "./data/matches_2018_2019.csv"
    matches2 = "./data/matches_2019_2020.csv"
    matches3 = "./data/matches_2020_2021.csv"
    referees = "./data/referees.csv"
    statusdata = "./data/status.csv"
    matches = [matches1, matches2, matches3]


    ### read from csv ###

    # read divisions
    with open(divisions) as fp:
        reader = csv.reader(fp, delimiter=",")
        next(reader, None)  # skip headers
        for row in reader:
            division_name = row[1]
            db.session.add(Division(division_name=division_name))
    db.session.commit()

    # read referees
    with open(referees) as fp:
        reader = csv.reader(fp, delimiter=",")
        next(reader, None)  # skip headers
        for row in reader:
            first_name = row[0]
            last_name = row[1]
            address = row[2]
            zip_code = int(row[3])
            city = row[4]
            phone_number = row[5]
            email = row[6]
            date_of_birth = row[7]
            db.session.add(Referee(first_name, last_name, address, zip_code, city, phone_number, email, date_of_birth))
    db.session.commit()

    # read status
    with open(statusdata) as fp:
        reader = csv.reader(fp, delimiter=",")
        next(reader, None)  # skip headers
        for row in reader:
            status_name = row[1]
            db.session.add(Status(status_name))
    db.session.commit()

    # read matches
    for match in matches:
        with open(match) as fp:
            reader = csv.reader(fp, delimiter=",")
            next(reader, None)  # skip headers
            for row in reader:
                division_id = int(row[0])
                matchweek = int(row[1])
                date = row[2]
                time = row[3]
                home_team_id = int(row[4])
                away_team_id = int(row[5])
                goals_home_team = int(row[6]) if row[6] != "NULL" else None
                goals_away_team = int(row[7]) if row[7] != "NULL" else None
                status = int(row[8]) if row[8] != "NULL" else None
                db.session.add(Match(division_id, matchweek, date, time, home_team_id, away_team_id, goals_home_team,
                                     goals_away_team, status))
        db.session.commit()

if __name__ == '__main__':
    cli()
