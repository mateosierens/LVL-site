# services/users/project/api/users.py
# CRUD operations for users

from flask import Blueprint, jsonify, request, render_template
from sqlalchemy import exc

from project.api.models import User
from project import db

users_blueprint = Blueprint('users', __name__, template_folder='./templates')

# create user
@users_blueprint.route('/users', methods=['POST'])
def add_user():
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    if not post_data:
        return jsonify(response_object), 400
    username = post_data.get('username')
    password = post_data.get('password')
    email = post_data.get('email')
    club = post_data.get('club')
    admin = post_data.get('admin')
    try:
        user = User.query.filter_by(email=email).first()
        if not user:
            db.session.add(User(username=username, password=password, email=email, club=club, admin=admin))
            db.session.commit()
            response_object['status'] = 'success'
            response_object['message'] = f'{email} was added!'
            return jsonify(response_object), 201
        else:
            response_object['message'] = 'Sorry. That email already exists.'
            return jsonify(response_object), 400
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400

# read user (by ID)
@users_blueprint.route('/users/<user_id>', methods=['GET'])
def get_single_user(user_id):
    """Get single user details"""
    response_object = {
        'status': 'fail',
        'message': 'User does not exist'
    }
    try:
        user = User.query.filter_by(id=int(user_id)).first()
        if not user:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                    'id': user.id,
                    'username': user.username,
                    'password': user.password,
                    'email': user.email,
                    'club': user.club,
                    'admin': user.admin
                }
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404

# read all users
@users_blueprint.route('/users', methods=['GET'])
def get_all_users():
    """Get all users"""
    response_object = {
        'status': 'success',
        'data': {
            'users': [user.to_json() for user in User.query.all()]
        }
    }
    return jsonify(response_object), 200

# update user
@users_blueprint.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Update single user details"""
    data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'User does not exist'
    }
    try:
        user = User.query.filter_by(id=int(user_id)).first()
        if not user:
            return jsonify(response_object), 404
        else:
            if not data:
                response_object['message'] = 'Invalid payload.'
                return jsonify(response_object), 400
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')
            club = data.get('club')
            admin = data.get('admin')
            findEmail = User.query.filter_by(email=email).first()
            if findEmail:
                response_object['message'] = 'Sorry. That email already exists.'
                return jsonify(response_object), 400
            user.username = username
            user.password = password
            user.email = email
            user.club = club
            user.admin = admin
            response_object = {
                'status': 'success',
                'message': 'User updated.'
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404
    except exc.IntegrityError as e:
        db.session.rollback()
        response_object['message'] = 'Invalid input data'
        return jsonify(response_object), 400

# delete user
@users_blueprint.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete single user by ID"""
    response_object = {
        'status': 'fail',
        'message': 'User does not exist'
    }
    try:
        user = User.query.filter_by(id=int(user_id)).first()
        if not user:
            return jsonify(response_object), 404
        else:
            User.query.filter_by(id=int(user_id)).delete()
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': 'User deleted'
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404
    except exc.IntegrityError as e:
        db.session.rollback()
        response_object['message'] = 'Failed to delete user'
        return jsonify(response_object), 400


