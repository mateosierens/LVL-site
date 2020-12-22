# services/users/manage.py

import unittest
import csv

from flask.cli import FlaskGroup

from project import create_app, db
from project.api.models import Club, Team

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
    teams = "../../data/teams.csv"
    clubs = "../../data/clubs.csv"

    # read from csv
    with open(clubs) as fp:
        reader = csv.reader(fp, delimiter=",")
        next(reader, None)  # skip headers
        for row in reader:
            stamNumber = int(row[0])
            name = row[1]
            address = row[2]
            zipCode = int(row[3])
            city = row[4]
            website = row[5] if row[5] != '' else None
            db.session.add(Club(stamNumber=stamNumber, name=name, address=address,
                                zipCode=zipCode, city=city, website=website))
    db.session.commit()

    # read from csv
    with open(teams) as fp:
        reader = csv.reader(fp, delimiter=",")
        next(reader, None)  # skip headers
        for row in reader:
            stamNumber = int(row[1])
            suffix = row[2] if row[2] != '' else None
            color = row[3]
            db.session.add(Team(stamNumber=stamNumber, suffix=suffix, color=color))
    db.session.commit()

if __name__ == '__main__':
    cli()
