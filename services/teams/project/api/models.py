# services/teams/project/api/models.py


from sqlalchemy.sql import func
from project import db

class Club(db.Model):
    __tablename__ = 'club'

    stamNumber = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String(128), nullable=False)
    zipCode = db.Column(db.Integer, nullable=False)
    city = db.Column(db.String(128), nullable=False)
    website = db.Column(db.String(128), nullable=True)
    teams = db.relationship("Team", back_populates="club", cascade="all, delete", passive_deletes=True)

    def __init__(self, stamNumber, name, address, zipCode, city, website):
        self.stamNumber = stamNumber
        self.name = name
        self.address = address
        self.zipCode = zipCode
        self.city = city
        self.website = website

    def to_json(self):
        return {
            'stamnumber': self.stamNumber,
            'name': self.name,
            'address': self.address,
            'zipcode': self.zipCode,
            'city': self.city,
            'website': self.website
        }

class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stamNumber = db.Column(db.Integer, db.ForeignKey(Club.stamNumber, ondelete="CASCADE"), nullable=False)
    suffix = db.Column(db.String(128), nullable=True)
    color = db.Column(db.String(128), nullable=False)
    club = db.relationship("Club", back_populates="teams")

    def __init__(self, stamNumber, suffix, color):
        self.stamNumber = stamNumber
        self.suffix = suffix
        self.color = color

    def to_json(self):
        return {
            'id': self.id,
            'stamnumber': self.stamNumber,
            'suffix': self.suffix,
            'color': self.color
        }