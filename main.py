from front_office_football_service import front_office_football_service
from team_service import team_service
from game_service import game_service

front_office_service = front_office_football_service()

game_service = game_service()
# game_service.get_play_result(4)
# game_service.get_offensive_play_personnel(3)
# game_service.get_defensive_play_personnel(3)
game_service.get_player_performance_from_play(3, 2, False)

# print(front_office_service.get_roster())
# this is a flask application - run the below command to start as a localhost
    # flask --app flaskr run