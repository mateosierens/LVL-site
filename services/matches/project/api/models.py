# services/matches/project/api/models.py


from sqlalchemy.sql import func
from project import db

class Referee(db.Models):
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

class Division(db.Models):
    __tablename__ = 'division'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    division_name = db.Column(db.String(128), nullable=False)

class Status(db.Models):
    __tablename__ = 'status'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status_name = db.Column(db.String(128), nullable=False)

class Match(db.Models):
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
