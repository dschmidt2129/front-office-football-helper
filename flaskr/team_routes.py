from flask import Blueprint
from flask import request
from team_service import team_service as ts

# class team_routes:
team_routes = Blueprint("team_routes", __name__)

@team_routes.route('/teamId')
def get_team_id():
    team_service = ts()
    team_info = team_service.get_team_id(request.args.get('teamName'))
    return str(team_info)