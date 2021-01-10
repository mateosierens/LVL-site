# services/teams/project/api/teams.py
# CRUD operations for teams and clubs

from flask import Blueprint, jsonify, request, render_template
from sqlalchemy import exc

from project.api.models import Team, Club
from project import db

teams_blueprint = Blueprint('teams', __name__)

### TEAMS ###
# ping
@teams_blueprint.route('/teams/ping', methods=['GET'])
def ping_team():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })

# create team
@teams_blueprint.route('/teams', methods=['POST'])
def add_team():
    """Create a team"""
    post_data = request.form
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    if not post_data:
        return jsonify(response_object), 400
    stamNumber = int(post_data.get('stamnumber'))
    suffix = post_data.get('suffix')
    color = post_data.get('color')
    try:
        club = Club.query.filter_by(stamNumber=stamNumber).first()
        if club:
            db.session.add(Team(stamNumber=stamNumber, suffix=suffix, color=color))
            db.session.commit()
            response_object['status'] = 'success'
            response_object['message'] = 'Team successfully created!'
            return jsonify(response_object), 201
        else:
            response_object['message'] = 'No club found with that stamnumber.'
            return jsonify(response_object), 400
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400

# get single team (by ID)
@teams_blueprint.route('/teams/<team_id>', methods=['GET'])
def get_single_team(team_id):
    """Get single team details"""
    response_object = {
        'status': 'fail',
        'message': 'Team does not exist'
    }
    try:
        team = Team.query.filter_by(id=int(team_id)).first()
        if not team:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                    'id': team.id,
                    'stamnumber': team.stamNumber,
                    'suffix': team.suffix,
                    'color': team.color
                }
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404

# get all teams
@teams_blueprint.route('/teams', methods=['GET'])
def get_all_teams():
    """Get all teams"""
    response_object = {
        'status': 'success',
        'data': {
            'teams': [team.to_json() for team in Team.query.all()]
        }
    }
    return jsonify(response_object), 200

# update team
@teams_blueprint.route('/teams/<team_id>', methods=['PUT'])
def update_team(team_id):
    """Update single team details"""
    data = request.form
    response_object = {
        'status': 'fail',
        'message': 'Team does not exist'
    }
    try:
        team = Team.query.filter_by(id=int(team_id)).first()
        if not team:
            return jsonify(response_object), 404
        else:
            if not data:
                response_object['message'] = 'Invalid payload.'
                return jsonify(response_object), 400
            stamNumber = int(data.get('stamnumber'))
            suffix = data.get('suffix')
            color = data.get('color')
            club = Club.query.filter_by(stamNumber=stamNumber).first()
            if not club:
                response_object['message'] = 'No club found with that stamnumber.'
                return jsonify(response_object), 400
            team.stamNumber = stamNumber
            team.suffix = suffix
            team.color = color
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': 'Team updated.'
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404
    except exc.IntegrityError as e:
        db.session.rollback()
        response_object['message'] = 'Invalid input data'
        return jsonify(response_object), 400

# delete team
@teams_blueprint.route('/teams/<team_id>', methods=['DELETE'])
def delete_team(team_id):
    """Delete single team by ID"""
    response_object = {
        'status': 'fail',
        'message': 'Team does not exist'
    }
    try:
        team = Team.query.filter_by(id=int(team_id)).first()
        if not team:
            return jsonify(response_object), 404
        else:
            Team.query.filter_by(id=int(team_id)).delete()
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': 'Team deleted'
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404
    except exc.IntegrityError as e:
        db.session.rollback()
        response_object['message'] = 'Failed to delete team'
        return jsonify(response_object), 400



### CLUBS ###
# ping
@teams_blueprint.route('/clubs/ping', methods=['GET'])
def ping_club():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })

# create club
@teams_blueprint.route('/clubs', methods=['POST'])
def add_club():
    """Create a club"""
    post_data = request.form
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    if not post_data:
        return jsonify(response_object), 400
    stamNumber = post_data.get('stamnumber')
    name = post_data.get('name')
    address = post_data.get('address')
    zipCode = post_data.get('zipcode')
    city = post_data.get('city')
    website = post_data.get('website')
    try:
        db.session.add(Club(stamNumber=stamNumber, name=name, address=address,
                            zipCode=zipCode, city=city, website=website))
        db.session.commit()
        response_object['status'] = 'success'
        response_object['message'] = 'Club successfully created!'
        return jsonify(response_object), 201
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400

# Read single club (by ID)
@teams_blueprint.route('/clubs/<club_id>', methods=['GET'])
def get_single_club(club_id):
    """Get single club details"""
    response_object = {
        'status': 'fail',
        'message': 'Club does not exist'
    }
    try:
        club = Club.query.filter_by(stamNumber=int(club_id)).first()
        if not club:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                    'stamnumber': club.stamNumber,
                    'name': club.name,
                    'address': club.address,
                    'zipcode': club.zipCode,
                    'city': club.city,
                    'website': club.website
                }
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404

# Read all clubs
@teams_blueprint.route('/clubs', methods=['GET'])
def get_all_clubs():
    """Get all clubs"""
    response_object = {
        'status': 'success',
        'data': {
            'clubs': [club.to_json() for club in Club.query.all()]
        }
    }
    return jsonify(response_object), 200

# update club
@teams_blueprint.route('/clubs/<club_id>', methods=['PUT'])
def update_club(club_id):
    """Update single club details"""
    data = request.form
    response_object = {
        'status': 'fail',
        'message': 'Club does not exist'
    }
    try:
        club = Club.query.filter_by(stamNumber=int(club_id)).first()
        if not club:
            return jsonify(response_object), 404
        else:
            if not data:
                response_object['message'] = 'Invalid payload.'
                return jsonify(response_object), 400
            club.stamNumber = data.get('stamnumber')
            club.name = data.get('name')
            club.address = data.get('address')
            club.city = data.get('city')
            club.zipCode = data.get('zipcode')
            club.website = data.get('website')
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': 'Club updated.'
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404
    except exc.IntegrityError as e:
        db.session.rollback()
        response_object['message'] = 'Invalid input data'
        return jsonify(response_object), 400

# delete club
@teams_blueprint.route('/clubs/<club_id>', methods=['DELETE'])
def delete_club(club_id):
    """Delete single club by ID"""
    response_object = {
        'status': 'fail',
        'message': 'Club does not exist'
    }
    try:
        club = Club.query.filter_by(stamNumber=int(club_id)).first()
        if not club:
            return jsonify(response_object), 404
        else:
            Club.query.filter_by(stamNumber=int(club_id)).delete()
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': 'Club deleted'
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404
    except exc.IntegrityError as e:
        db.session.rollback()
        response_object['message'] = 'Failed to delete club'
        return jsonify(response_object), 400

