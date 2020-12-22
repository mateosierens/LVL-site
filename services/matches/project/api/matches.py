# services/teams/project/api/matches.py
# CRUD operations for matches and referees

from flask import Blueprint, jsonify, request, render_template
from sqlalchemy import exc

from project.api.models import Referee, Status, Division, Match
from project import db

matches_blueprint = Blueprint('matches', __name__)



