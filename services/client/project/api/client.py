# services/client/project/api/client.py
# front end of the site

from flask import Blueprint, jsonify, request, render_template
from sqlalchemy import exc
from sqlalchemy.sql import func

# from project.api.models import Referee, Status, Division, Match
from project import db

client_blueprint = Blueprint('client', __name__, template_folder='./templates')


@client_blueprint.route('/', methods=['GET'])
def home():
    return render_template('home.html')