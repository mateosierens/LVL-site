# services/client/project/api/client.py
# front end of the site
import requests

from flask import Blueprint, jsonify, request, render_template, redirect, url_for, make_response
from sqlalchemy import exc
from sqlalchemy.sql import func

# from project.api.models import Referee, Status, Division, Match
from project import db, create_app, jwt

from flask_jwt_extended import (
    jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies, verify_jwt_in_request_optional
)

client_blueprint = Blueprint('client', __name__, template_folder='./templates')

# helper function to check login
def get_identity_if_login():
    try:
        verify_jwt_in_request_optional()
        return get_jwt_identity()
    except Exception:
        pass


@client_blueprint.route('/', methods=['GET'])
def home():
    user = get_identity_if_login()
    if user:
        return render_template('home.html', login=True, admin=user['admin'])
    else:
        return render_template('home.html', login=False, admin=False)

@client_blueprint.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    # check if user exists
    response = requests.get("http://users:5000/users")
    data = response.json()['data']['users']

    found = False
    foundUser = None
    for user in data:
        if user['username'] == username and user['password'] == password:
            found = True
            foundUser = user
            break

    # wrong credentials:
    if not found:
        return render_template('login.html', badLogin=True)

    # Create the tokens we will be sending back to the user
    access_token = create_access_token(identity=foundUser)
    refresh_token = create_refresh_token(identity=foundUser)

    resp = redirect(url_for('client.home'))
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp

# Same thing as login here, except we are only setting a new cookie
# for the access token.
@client_blueprint.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    # Create the new access token
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)

    # Set the JWT access cookie in the response
    resp = jsonify({'refresh': True})
    set_access_cookies(resp, access_token)
    return resp, 200


@client_blueprint.route('/login', methods=['GET'])
def get_login_page():
    return render_template('login.html', badLogin=False)

@client_blueprint.route('/logout', methods=['GET'])
def logout():
    resp = make_response(render_template('logout_success.html'))
    unset_jwt_cookies(resp)
    return resp, 200

