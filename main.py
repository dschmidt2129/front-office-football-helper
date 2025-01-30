from front_office_football_service import front_office_football_service
from team_service import team_service
from game_service import game_service

front_office_service = front_office_football_service()

game_service = game_service()
game_service.get_player_performance_from_play(1, 1, False)

# this is a flask application - run the below command to start as a localhost
    # flask --app flaskr run