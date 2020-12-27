# services/matches/project/api/matches.py
# CRUD operations for matches and referees

from flask import Blueprint, jsonify, request, render_template
from sqlalchemy import exc
from sqlalchemy.sql import func

from project.api.models import Referee, Status, Division, Match
from project import db

matches_blueprint = Blueprint('matches', __name__)


### REFEREE ###
# ping
@matches_blueprint.route('/referees/ping', methods=['GET'])
def ping_referees():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })


# create
@matches_blueprint.route('/referees', methods=['POST'])
def add_referee():
    """Create a referee"""
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    if not post_data:
        return jsonify(response_object), 400
    first_name = post_data.get('firstname')
    last_name = post_data.get('lastname')
    address = post_data.get('address')
    zip_code = post_data.get('zipcode')
    city = post_data.get('city')
    phone_number = post_data.get('phonenumber')
    email = post_data.get('email')
    birth_date = post_data.get('birthdate')
    try:
        db.session.add(Referee(first_name, last_name, address, zip_code, city, phone_number, email, birth_date))
        db.session.commit()
        response_object['status'] = 'success'
        response_object['message'] = 'Referee successfully created!'
        return jsonify(response_object), 201
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


# read
# get single referee (by ID)
@matches_blueprint.route('/referees/<referee_id>', methods=['GET'])
def get_single_referee(referee_id):
    """Get single referee details"""
    response_object = {
        'status': 'fail',
        'message': 'Referee does not exist'
    }
    try:
        referee = Referee.query.filter_by(id=int(referee_id)).first()
        if not referee:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                    'id': referee.id,
                    'firstname': referee.first_name,
                    'lastname': referee.last_name,
                    'address': referee.address,
                    'zipcode': referee.zip_code,
                    'city': referee.city,
                    'phonenumber': referee.phone_number,
                    'email': referee.email,
                    'birthdate': referee.birth_date.strftime('%Y-%m-%d')
                }
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404


# get all referees
@matches_blueprint.route('/referees', methods=['GET'])
def get_all_referees():
    """Get all referees"""
    response_object = {
        'status': 'success',
        'data': {
            'referees': [referee.to_json() for referee in Referee.query.all()]
        }
    }
    return jsonify(response_object), 200


# update
@matches_blueprint.route('/referees/<referee_id>', methods=['PUT'])
def update_referee(referee_id):
    """Update single referee details"""
    data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Referee does not exist'
    }
    try:
        referee = Referee.query.filter_by(id=int(referee_id)).first()
        if not referee:
            return jsonify(response_object), 404
        else:
            if not data:
                response_object['message'] = 'Invalid payload.'
                return jsonify(response_object), 400
            referee.first_name = data.get('firstname')
            referee.last_name = data.get('lastname')
            referee.address = data.get('address')
            referee.zip_code = data.get('zipcode')
            referee.city = data.get('city')
            referee.phone_number = data.get('phonenumber')
            referee.email = data.get('email')
            referee.birth_date = data.get('birthdate')
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': 'Referee updated.'
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404
    except exc.IntegrityError as e:
        db.session.rollback()
        response_object['message'] = 'Invalid input data'
        return jsonify(response_object), 400


# delete
@matches_blueprint.route('/referees/<referee_id>', methods=['DELETE'])
def delete_referee(referee_id):
    """Delete single referee by ID"""
    response_object = {
        'status': 'fail',
        'message': 'Referee does not exist'
    }
    try:
        referee = Referee.query.filter_by(id=int(referee_id)).first()
        if not referee:
            return jsonify(response_object), 404
        else:
            Referee.query.filter_by(id=int(referee_id)).delete()
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': 'Referee deleted'
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404
    except exc.IntegrityError as e:
        db.session.rollback()
        response_object['message'] = 'Failed to delete referee'
        return jsonify(response_object), 400


### DIVISION ###
# ping
@matches_blueprint.route('/divisions/ping', methods=['GET'])
def ping_divisions():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })


# create
@matches_blueprint.route('/divisions', methods=['POST'])
def add_division():
    """Create a division"""
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    if not post_data:
        return jsonify(response_object), 400
    division_name = post_data.get('divisionname')
    try:
        db.session.add(Division(division_name))
        db.session.commit()
        response_object['status'] = 'success'
        response_object['message'] = 'Division successfully created!'
        return jsonify(response_object), 201
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


# read
# get single division (by ID)
@matches_blueprint.route('/divisions/<division_id>', methods=['GET'])
def get_single_division(division_id):
    """Get single division details"""
    response_object = {
        'status': 'fail',
        'message': 'Division does not exist'
    }
    try:
        division = Division.query.filter_by(id=int(division_id)).first()
        if not division:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                    'id': division.id,
                    'divisionname': division.division_name
                }
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404


# get all divisions
@matches_blueprint.route('/divisions', methods=['GET'])
def get_all_divisions():
    """Get all divisions"""
    response_object = {
        'status': 'success',
        'data': {
            'divisions': [division.to_json() for division in Division.query.all()]
        }
    }
    return jsonify(response_object), 200


# update
@matches_blueprint.route('/divisions/<division_id>', methods=['PUT'])
def update_division(division_id):
    """Update single division details"""
    data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Division does not exist'
    }
    try:
        division = Division.query.filter_by(id=int(division_id)).first()
        if not division:
            return jsonify(response_object), 404
        else:
            if not data:
                response_object['message'] = 'Invalid payload.'
                return jsonify(response_object), 400
            division.division_name = data.get('divisionname')
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': 'Division updated.'
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404
    except exc.IntegrityError as e:
        db.session.rollback()
        response_object['message'] = 'Invalid input data'
        return jsonify(response_object), 400


# delete
@matches_blueprint.route('/divisions/<division_id>', methods=['DELETE'])
def delete_division(division_id):
    """Delete single division by ID"""
    response_object = {
        'status': 'fail',
        'message': 'Division does not exist'
    }
    try:
        division = Division.query.filter_by(id=int(division_id)).first()
        if not division:
            return jsonify(response_object), 404
        else:
            # check if there is a match containing division id, if so return error
            match = Match.query.filter_by(division_id=division_id).first()
            if match:
                response_object['message'] = 'Failed to delete division: division still has existing matches'
                return jsonify(response_object), 400
            Division.query.filter_by(id=int(division_id)).delete()
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': 'Division deleted'
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404
    except exc.IntegrityError as e:
        db.session.rollback()
        response_object['message'] = 'Failed to delete division'
        return jsonify(response_object), 400


### STATUS ###
# ping
@matches_blueprint.route('/status/ping', methods=['GET'])
def ping_status():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })


# create
@matches_blueprint.route('/status', methods=['POST'])
def add_status():
    """Create a status"""
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    if not post_data:
        return jsonify(response_object), 400
    status_name = post_data.get('statusname')
    try:
        db.session.add(Status(status_name))
        db.session.commit()
        response_object['status'] = 'success'
        response_object['message'] = 'Status successfully created!'
        return jsonify(response_object), 201
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


# read
# get single status (by ID)
@matches_blueprint.route('/status/<status_id>', methods=['GET'])
def get_single_status(status_id):
    """Get single status details"""
    response_object = {
        'status': 'fail',
        'message': 'Status does not exist'
    }
    try:
        status = Status.query.filter_by(id=int(status_id)).first()
        if not status:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                    'id': status.id,
                    'statusname': status.status_name
                }
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404


# get all status
@matches_blueprint.route('/status', methods=['GET'])
def get_all_status():
    """Get all status"""
    response_object = {
        'status': 'success',
        'data': {
            'status': [status.to_json() for status in Status.query.all()]
        }
    }
    return jsonify(response_object), 200


# update
@matches_blueprint.route('/status/<status_id>', methods=['PUT'])
def update_status(status_id):
    """Update single status details"""
    data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Status does not exist'
    }
    try:
        status = Status.query.filter_by(id=int(status_id)).first()
        if not status:
            return jsonify(response_object), 404
        else:
            if not data:
                response_object['message'] = 'Invalid payload.'
                return jsonify(response_object), 400
            status.status_name = data.get('statusname')
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': 'Status updated.'
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404
    except exc.IntegrityError as e:
        db.session.rollback()
        response_object['message'] = 'Invalid input data'
        return jsonify(response_object), 400


# delete
@matches_blueprint.route('/status/<status_id>', methods=['DELETE'])
def delete_status(status_id):
    """Delete single status by ID"""
    response_object = {
        'status': 'fail',
        'message': 'Status does not exist'
    }
    try:
        status = Status.query.filter_by(id=int(status_id)).first()
        if not status:
            return jsonify(response_object), 404
        else:
            Status.query.filter_by(id=int(status_id)).delete()
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': 'Status deleted'
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404
    except exc.IntegrityError as e:
        db.session.rollback()
        response_object['message'] = 'Failed to delete status'
        return jsonify(response_object), 400


### MATCH ###
# ping
@matches_blueprint.route('/matches/ping', methods=['GET'])
def ping_matches():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })


# create
@matches_blueprint.route('/matches', methods=['POST'])
def add_match():
    """Create a match"""
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    if not post_data:
        return jsonify(response_object), 400
    division = post_data.get('division')
    matchweek = post_data.get('matchweek')
    date = post_data.get('date')
    time = post_data.get('time')
    hometeam = post_data.get('hometeam')
    awayteam = post_data.get('awayteam')
    goalshome = post_data.get('goalshome')
    goalsaway = post_data.get('goalsaway')
    status = post_data.get('status')
    referee = None
    if 'referee' in post_data:
        referee = post_data.get('referee')
    try:
        if referee is not None:
            toCheck = Match.query.filter_by(referee=referee).all()
            for match in toCheck:
                match_json = match.to_json()
                if match_json['date'] == date and match_json['time'] == time:
                    response_object['message'] = 'Referee double booked'
                    return jsonify(response_object), 400
        db.session.add(
            Match(division, matchweek, date, time, hometeam, awayteam, goalshome, goalsaway, status, referee))
        db.session.commit()
        response_object['status'] = 'success'
        response_object['message'] = 'Match successfully created!'
        return jsonify(response_object), 201
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


# read
# get single match (by ID)
@matches_blueprint.route('/matches/<match_id>', methods=['GET'])
def get_single_match(match_id):
    """Get single match details"""
    response_object = {
        'status': 'fail',
        'message': 'Match does not exist'
    }
    try:
        match = Match.query.filter_by(id=int(match_id)).first()
        if not match:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                    'id': match.id,
                    'division': match.division_id,
                    'matchweek': match.matchweek,
                    'date': match.date.strftime('%Y-%m-%d'),
                    'time': match.time.strftime('%H:%M:%S'),
                    'hometeam': match.home_team_id,
                    'awayteam': match.away_team_id,
                    'goalshome': match.goals_home_team,
                    'goalsaway': match.goals_away_team,
                    'status': match.status,
                    'referee': match.referee
                }
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404


# get all matches
@matches_blueprint.route('/matches', methods=['GET'])
def get_all_matches():
    """Get all matches"""
    response_object = {
        'status': 'success',
        'data': {
            'matches': [match.to_json() for match in Match.query.all()]
        }
    }
    return jsonify(response_object), 200


# update
@matches_blueprint.route('/matches/<match_id>', methods=['PUT'])
def update_match(match_id):
    """Update single match details"""
    data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Match does not exist'
    }
    try:
        match = Match.query.filter_by(id=int(match_id)).first()
        if not match:
            return jsonify(response_object), 404
        else:
            if not data:
                response_object['message'] = 'Invalid payload.'
                return jsonify(response_object), 400
            referee = None
            if 'referee' in data:
                referee = data.get('referee')
            if referee is not None:
                toCheck = Match.query.filter_by(referee=referee).all()
                for match in toCheck:
                    match_json = match.to_json()
                    if match_json['date'] == data.get('date') and match_json['time'] == data.get('time'):
                        response_object['message'] = 'Referee double booked'
                        return jsonify(response_object), 400
            match.division = data.get('division')
            match.matchweek = data.get('matchweek')
            match.date = data.get('date')
            match.time = data.get('time')
            match.hometeam = data.get('hometeam')
            match.awayteam = data.get('awayteam')
            match.goalshome = data.get('goalshome')
            match.goalsaway = data.get('goalsaway')
            match.status = data.get('status')
            match.referee = referee
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': 'Match updated.'
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404
    except exc.IntegrityError as e:
        db.session.rollback()
        response_object['message'] = 'Invalid input data'
        return jsonify(response_object), 400


# delete
@matches_blueprint.route('/matches/<match_id>', methods=['DELETE'])
def delete_match(match_id):
    """Delete single match by ID"""
    response_object = {
        'status': 'fail',
        'message': 'Match does not exist'
    }
    try:
        match = Match.query.filter_by(id=int(match_id)).first()
        if not match:
            return jsonify(response_object), 404
        else:
            Match.query.filter_by(id=int(match_id)).delete()
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': 'Match deleted'
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404
    except exc.IntegrityError as e:
        db.session.rollback()
        response_object['message'] = 'Failed to delete match'
        return jsonify(response_object), 400
