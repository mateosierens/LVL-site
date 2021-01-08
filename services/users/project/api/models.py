# services/users/project/api/models.py


from sqlalchemy.sql import func
from project import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    club = db.Column(db.String(128), nullable=True)
    admin = db.Column(db.Boolean(), default=False, nullable=False)
    super_admin = db.Column(db.Boolean(), default=False, nullable=False)

    def __init__(self, username, password, email, club, admin, super_admin):
        self.username = username
        self.password = password
        self.email = email
        self.club = club
        self.admin = admin
        self.super_admin = admin

    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'club': self.club,
            'admin': self.admin,
            'superadmin': self.super_admin
        }