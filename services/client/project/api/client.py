# services/client/project/api/client.py
# front end of the site
import requests
import datetime
from math import inf
import json

from flask import Blueprint, jsonify, request, render_template, redirect, url_for, make_response
from sqlalchemy import exc
from sqlalchemy.sql import func

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
        return render_template('home.html', login=True, userclub=user['club'], admin=user['admin'])
    else:
        return render_template('home.html', login=False, userclub=None, admin=False)


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
    return render_template('login.html', badLogin=False, userclub=None)


@client_blueprint.route('/logout', methods=['GET'])
def logout():
    resp = make_response(render_template('logout_success.html', userclub=None))
    unset_jwt_cookies(resp)
    return resp, 200


@client_blueprint.route('/competition/clubs', methods=['GET'])
def get_all_clubs():
    # get list of clubs info and pass this to html template
    response = requests.get("http://teams:5000/clubs")
    data = response.json()['data']['clubs']

    user = get_identity_if_login()
    if user:
        return render_template('clubs.html', login=True, userclub=user['club'], admin=user['admin'], data=data)
    else:
        return render_template('clubs.html', login=False, userclub=None, admin=False, data=data)


@client_blueprint.route('/competition/clubs/<stamnumber>', methods=['GET'])
def get_club(stamnumber):
    # get list of clubs info and pass this to html template
    response = requests.get(f"http://teams:5000/clubs/{stamnumber}")
    club = response.json()['data']

    response = requests.get("http://teams:5000/teams")
    teams = response.json()['data']['teams']

    user = get_identity_if_login()
    if user:
        return render_template('club.html', login=True, userclub=user['club'], club=club, admin=user['admin'],
                               teams=teams)
    else:
        return render_template('club.html', login=False, userclub=None, club=club, admin=False, teams=teams)


def getLastGames(matches, amount=3):
    to_return = []
    list_copy = matches[:]
    for i in range(amount):
        val = min(list_copy,
                  key=lambda s: datetime.datetime.strptime(s['date'], "%Y-%m-%d").date() - datetime.date.today())
        to_return.append(val)
        list_copy.remove(val)
    return to_return


def create_win_loss_string(games, team):
    string = ""
    for game in games:
        if game['goalshome'] > game['goalsaway']:
            if team == game['hometeam']:
                string += 'W'
            else:
                string += 'L'
        elif game['goalshome'] == game['goalsaway']:
            string += 'D'
        else:
            if team == game['hometeam']:
                string += 'L'
            else:
                string += 'W'
    return string


@client_blueprint.route('/competition/teams/<team_id>', methods=['GET'])
def get_team(team_id):
    # get team
    response = requests.get(f"http://teams:5000/teams/{team_id}")
    team = response.json()['data']

    # get club with stamnumber of team
    response = requests.get(f"http://teams:5000/clubs/{team['stamnumber']}")
    club = response.json()['data']

    # make fixture for upcoming matches
    # get all matches
    response = requests.get("http://matches:5000/matches")
    matches = response.json()['data']['matches']

    upcoming_matches = []
    today = datetime.date.today()
    for match in matches:
        date = datetime.datetime.strptime(match['date'], '%Y-%m-%d').date()
        if date >= today and (match['hometeam'] == team['id'] or match['awayteam'] == team['id']):
            upcoming_matches.append(match)
    fixture = make_week_fixture(upcoming_matches)

    team_matches = []
    for match in matches:
        if match['hometeam'] == team['id'] or match['awayteam'] == team['id']:
            team_matches.append(match)

    last_results = getLastGames(team_matches)
    string = create_win_loss_string(last_results, team_id)

    user = get_identity_if_login()
    if user:
        return render_template('team.html', login=True, admin=user['admin'], userclub=user['club'], team=team,
                               club=club,
                               fixture=fixture,
                               string=string)
    else:
        return render_template('team.html', login=False, admin=False, team=team, userclub=None, club=club,
                               fixture=fixture,
                               string=string)


@client_blueprint.route('/competition/divisions', methods=['GET'])
def get_divisions():
    # get divisions
    response = requests.get("http://matches:5000/divisions")
    divisions = response.json()['data']['divisions']

    user = get_identity_if_login()
    if user:
        return render_template('divisions.html', login=True, userclub=user['club'], admin=user['admin'],
                               divisions=divisions)
    else:
        return render_template('divisions.html', login=False, userclub=None, admin=False, divisions=divisions)


def getTeamName(team_id):
    resp = requests.get(f"http://teams:5000/teams/{team_id}")
    stamnumber = resp.json()['data']['stamnumber']
    resp = requests.get(f"http://teams:5000/clubs/{stamnumber}")
    return resp.json()['data']['name']


def getStatus(status_id):
    resp = requests.get(f"http://matches:5000/status/{status_id}")
    return resp.json()['data']['statusname']


def scoreGoals(team_id, matches):
    info = {'name': team_id, 'played': 0, 'win': 0, 'loss': 0, 'tie': 0, 'DV': 0, 'DT': 0, 'PT': 0, 'sheet': 0}
    for match in matches:
        if match['goalshome'] is None or match['goalsaway'] is None:
            continue
        if match['hometeam'] == team_id:
            info['played'] += 1
            info['DV'] += match['goalshome']
            info['DT'] += match['goalsaway']
            if info['DT'] == 0:
                info['sheet'] += 1
            if match['goalshome'] > match['goalsaway']:
                info['PT'] += 3
                info['win'] += 1
            elif match['goalshome'] == match['goalsaway']:
                info['PT'] += 1
                info['tie'] += 1
            else:
                info['loss'] += 1
        elif match['awayteam'] == team_id:
            info['played'] += 1
            info['DV'] += match['goalsaway']
            info['DT'] += match['goalshome']
            if info['DT'] == 0:
                info['sheet'] += 1
            if match['goalshome'] < match['goalsaway']:
                info['PT'] += 3
                info['win'] += 1
            elif match['goalshome'] == match['goalsaway']:
                info['PT'] += 1
                info['tie'] += 1
            else:
                info['loss'] += 1
    return info


def make_league_table(matches_division):
    """
    Creates the league table for a certain division, helper function for route function below
    :param matches_division: list of matches for a certain division
    :return: ordered list that specifies league table, each entry is dict
    """
    teams_checked = []  # list of teams checked
    ranking = []
    for match in matches_division:
        team_id = match['hometeam']
        if team_id not in teams_checked:
            rank = scoreGoals(team_id, matches_division)
            ranking.append(rank)
            teams_checked.append(team_id)
        else:
            team_id = match['awayteam']
            if team_id not in teams_checked:
                rank = scoreGoals(team_id, matches_division)
                ranking.append(rank)
                teams_checked.append(team_id)

    # sort ranking on score from high to low
    ranking.sort(key=lambda rank: rank['PT'], reverse=True)

    return ranking


def make_week_fixture(matches):
    week = []
    for match in matches:
        info = {}
        info['matchweek'] = match['matchweek']
        info['date'] = match['date']
        info['time'] = match['time']
        info['hometeam'] = getTeamName(match['hometeam'])
        info['awayteam'] = getTeamName(match['awayteam'])
        info['status'] = getStatus(match['status']) if match['status'] is not None else ''
        info['referee'] = match['referee'] if match['referee'] is not None else ''
        info['result'] = str(match['goalshome']) + ' - ' + str(match['goalsaway']) if match['goalshome'] is not None or \
                                                                                      match[
                                                                                          'goalsaway'] is not None else ''
        info['id'] = match['id']
        week.append(info)
    return week


@client_blueprint.route('/competition/divisions/<division_id>', methods=['GET'])
def get_fixture_for_division(division_id):
    # get all seasons
    seasons = []
    year0 = 2018
    year1 = 2019
    for i in range(3):
        seasons.append({'season': str(year0) + '-' + str(year1)})
        year0 += 1
        year1 += 1

    user = get_identity_if_login()
    if user:
        return render_template('seasons.html', login=True, userclub=user['club'], admin=user['admin'], seasons=seasons,
                               division=division_id)
    else:
        return render_template('seasons.html', login=False, userclub=None, admin=False, seasons=seasons,
                               division=division_id)


@client_blueprint.route('/competition/divisions/<division_id>/<year0>-<year1>', methods=['GET'])
def get_fixture_for_division_season(division_id, year0, year1):
    # get all matches
    response = requests.get("http://matches:5000/matches")
    matches = response.json()['data']['matches']

    # define season
    begin_season = datetime.date(int(year0), 9, 1)
    end_season = datetime.date(int(year1), 8, 31)

    # make league table
    division_matches = []
    for match in matches:
        date = datetime.datetime.strptime(match['date'], '%Y-%m-%d').date()
        if match['division'] == int(division_id) and begin_season <= date <= end_season:
            division_matches.append(match)
    league_table = make_league_table(division_matches)

    # convert team id into team name
    # list team with best attack, defense, most clean sheet
    best_attack = None
    best_attack_points = 0
    best_defense = None
    best_defense_points = inf
    cleanest_sheet = None
    cleanest_sheet_points = 0
    for entry in league_table:
        entry['name'] = getTeamName(entry['name'])
        if entry['DV'] > best_attack_points:
            best_attack_points = entry['DV']
            best_attack = entry
        if entry['DT'] < best_defense_points:
            best_defense_points = entry['DT']
            best_defense = entry
        if entry['sheet'] > cleanest_sheet_points:
            cleanest_sheet_points = entry['sheet']
            cleanest_sheet = entry

    # convert season to json for template
    year = {'begin': year0, 'end': year1}

    # show all fixtures for specific matchweek with posibility to filter on specific team
    # filter on matchweek
    matchweek = request.args.get('matchweek', default=None, type=int)

    # filter on team
    response = requests.get("http://teams:5000/clubs")
    clubs = response.json()['data']['clubs']
    team = request.args.get('team', default=None, type=str)

    # create fixture
    week_matches = []
    if matchweek == None:
        week_matches = division_matches
    else:
        for match in division_matches:
            if match['matchweek'] == matchweek:
                week_matches.append(match)
    fixture = make_week_fixture(week_matches)

    # filter fixture on team
    if team is not None:
        temp_fixture = []
        team.replace('+', ' ')
        for entry in fixture:
            if entry['hometeam'] == team or entry['awayteam'] == team:
                temp_fixture.append(entry)
        fixture = temp_fixture

    if fixture:
        # sort fixture on matchweek
        fixture.sort(key=lambda week: week['matchweek'])

    user = get_identity_if_login()
    if user:
        return render_template('league.html', login=True, userclub=user['club'], admin=user['admin'],
                               league_table=league_table, year=year,
                               fixture=fixture, clubs=clubs, best_attack=best_attack, best_defense=best_defense,
                               cleanest_sheet=cleanest_sheet)
    else:
        return render_template('league.html', login=False, userclub=None, admin=False, league_table=league_table,
                               year=year,
                               fixture=fixture, clubs=clubs, best_attack=best_attack, best_defense=best_defense,
                               cleanest_sheet=cleanest_sheet)


@client_blueprint.route('/competition/matches/<match_id>', methods=['GET'])
def get_specific_fixture(match_id):
    # normal info
    response = requests.get(f"http://matches:5000/matches/{match_id}")
    match = response.json()['data']

    # check if match is yet to be played
    # if true, include statistics
    date = datetime.datetime.strptime(match['date'], '%Y-%m-%d').date()
    now = datetime.date.today()
    stats = False
    times_played = 0
    wins_hometeam = 0
    wins_awayteam = 0
    last_games = []
    ht_scores_string = ''
    at_scores_string = ''
    if date > now:
        stats = True
        # match has not been played
        response = requests.get("http://matches:5000/matches")
        matches = response.json()['data']['matches']

        historic_matches = []
        for temp_match in matches:
            if (temp_match['hometeam'] == match['hometeam'] or temp_match['hometeam'] == match['awayteam']) and (
                    temp_match['awayteam'] == match['hometeam'] or temp_match['awayteam'] == match['awayteam']):
                if temp_match['goalshome'] is None or temp_match['goalsaway'] is None:
                    continue
                historic_matches.append(temp_match)
                times_played += 1
                if temp_match['goalshome'] > temp_match['goalsaway']:
                    if temp_match['hometeam'] == match['hometeam']:
                        wins_hometeam += 1
                    else:
                        wins_awayteam += 1
                elif temp_match['goalshome'] < temp_match['goalsaway']:
                    if temp_match['awayteam'] == match['hometeam']:
                        wins_hometeam += 1
                    else:
                        wins_awayteam += 1
        last_games = getLastGames(historic_matches)
        hometeam_matches = [i for i in matches if
                            i['hometeam'] == match['hometeam'] or i['awayteam'] == match['hometeam']]
        awayteam_matches = [i for i in matches if
                            i['hometeam'] == match['awayteam'] or i['awayteam'] == match['awayteam']]
        ht_last_games = getLastGames(hometeam_matches, 5)
        at_last_games = getLastGames(awayteam_matches, 5)
        ht_scores_string = create_win_loss_string(ht_last_games, match['hometeam'])
        at_scores_string = create_win_loss_string(at_last_games, match['awayteam'])

    # check if match is in 7 days, if so include weather report
    week = None
    next_week = now + datetime.timedelta(days=7)
    if now <= date <= next_week:
        # get weather info from antwerpen
        delta = date - now
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/onecall?lat=51.2194475&lon=4.4024643&exclude=current,minutely,hourly,alerts&units=metric&appid=0202a55647559a82e31a2b4711bfc638")
        week = response.json()['daily'][delta.days]

    # render template
    match['hometeam'] = getTeamName(match['hometeam'])
    match['awayteam'] = getTeamName(match['awayteam'])
    for game in last_games:
        game['hometeam'] = getTeamName(game['hometeam'])
        game['awayteam'] = getTeamName(game['awayteam'])

    user = get_identity_if_login()
    if user:
        return render_template('fixture.html', login=True, userclub=user['club'], admin=user['admin'], match=match,
                               stats=stats,
                               times_played=times_played, wins_awayteam=wins_awayteam, wins_hometeam=wins_hometeam,
                               last_games=last_games, ht_scores=ht_scores_string, at_scores=at_scores_string,
                               forecast=week)
    else:
        return render_template('fixture.html', login=False, userclub=None,
                               admin=False, match=match, stats=stats,
                               times_played=times_played, wins_awayteam=wins_awayteam, wins_hometeam=wins_hometeam,
                               last_games=last_games, ht_scores=ht_scores_string, at_scores=at_scores_string,
                               forecast=week)


@client_blueprint.route('/scores', methods=['GET'])
@jwt_required
def get_scores():
    user = get_identity_if_login()
    club = user['club']

    # get all teams of club
    response = requests.get(f'http://teams:5000/teams')
    teams = response.json()['data']['teams']

    team_ids = []
    for team in teams:
        if team['stamnumber'] == int(club):
            team_ids.append(team['id'])

    response = requests.get("http://matches:5000/matches")
    matches = response.json()['data']['matches']

    # user can edit all his home games
    to_show = []
    for match in matches:
        team_id = match['hometeam']
        if team_id in team_ids:
            to_show.append(match)

    for game in to_show:
        game['hometeam'] = getTeamName(game['hometeam'])
        game['awayteam'] = getTeamName(game['awayteam'])
        game['status'] = getStatus(match['status']) if match['status'] is not None else ''
        game['referee'] = game['referee'] if game['referee'] is not None else ''
        game['result'] = str(game['goalshome']) + ' - ' + str(game['goalsaway']) if game['goalshome'] is not None or \
                                                                                    game[
                                                                                        'goalsaway'] is not None else ''

    to_show.sort(key=lambda match: match['date'])

    return render_template('scores.html', login=True, userclub=user['club'], admin=user['admin'], matches=to_show)

@client_blueprint.route('/scores/<match_id>', methods=['GET'])
def score_form(match_id):
    user = get_identity_if_login()
    return render_template('score_form.html', login=True, userclub=user['club'], admin=user['admin'], match=match_id)


@client_blueprint.route('/scores/<match_id>', methods=['POST'])
@jwt_required
def post_scores(match_id):
    score = request.form.get('score')
    score = score.split('-')
    response = requests.get(f'http://matches:5000/matches/{match_id}')
    match = response.json()['data']

    match['goalshome'] = int(score[0])
    match['goalsaway'] = int(score[1])

    response = requests.put(f'http://matches:5000/matches/{match_id}', data=match)

    user = get_identity_if_login()
    return render_template('successful_score_update.html', login=True, userclub=user['club'], admin=user['admin'])

