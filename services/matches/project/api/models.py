# services/matches/project/api/models.py


from sqlalchemy.sql import func
from project import db

class Referee(db.Model):
    __tablename__ = 'referee'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String(128), nullable=False)
    zip_code = db.Column(db.Integer, nullable=False)
    city = db.Column(db.String(128), nullable=False)
    phone_number = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)

    def __init__(self, first_name, last_name, address, zip_code, city, phone_number, email, birth_date):
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.zip_code = zip_code
        self.city = city
        self.phone_number = phone_number
        self.email = email
        self.birth_date = birth_date

    def to_json(self):
        return {
            'id': self.id,
            'firstname': self.first_name,
            'lastname': self.last_name,
            'address': self.address,
            'zipcode': self.zip_code,
            'city': self.city,
            'phonenumber': self.phone_number,
            'email': self.email,
            'birthdate': self.birth_date
        }

class Division(db.Model):
    __tablename__ = 'division'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    division_name = db.Column(db.String(128), nullable=False)

    def __init__(self, division_name):
        self.division_name = division_name

    def to_json(self):
        return {
            'id': self.id,
            'divisionname': self.division_name
        }

class Status(db.Model):
    __tablename__ = 'status'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status_name = db.Column(db.String(128), nullable=False)

    def __init__(self, status_name):
        self.status_name = status_name

    def to_json(self):
        return {
            'id': self.id,
            'statusname': self.status_name
        }

class Match(db.Model):
    __tablename__ = 'match'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    division_id = db.Column(db.Integer, db.ForeignKey(Division.id), nullable=False)
    matchweek = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    home_team_id = db.Column(db.Integer, nullable=False)
    away_team_id = db.Column(db.Integer, nullable=False)
    goals_home_team = db.Column(db.Integer, nullable=True)
    goals_away_team = db.Column(db.Integer, nullable=True)
    status = db.Column(db.Integer, db.ForeignKey(Status.id, ondelete='SET NULL'), nullable=True)
    referee = db.Column(db.Integer, db.ForeignKey(Referee.id, ondelete='SET NULL'), default=None, nullable=True)

    def __init__(self, division_id, matchweek, date, time, home_team_id, away_team_id, goals_home_team,
                 goals_away_team, status):
        self.division_id = division_id
        self.matchweek = matchweek
        self.date = date
        self.time = time
        self.home_team_id = home_team_id
        self.away_team_id = away_team_id
        self.goals_home_team = goals_home_team
        self.goals_away_team = goals_away_team
        self.status = status

    def to_json(self):
        return {
            'id': self.id,
            'division': self.division_id,
            'matchweek': self.matchweek,
            'date': self.date,
            'time': self.time,
            'hometeam': self.home_team_id,
            'awayteam': self.away_team_id,
            'goalshome': self.goals_home_team,
            'goalsaway': self.goals_away_team,
            'status': self.status,
            'referee': self.referee
        }