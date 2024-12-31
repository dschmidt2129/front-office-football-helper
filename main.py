from front_office_football_service import front_office_football_service
from team_service import team_service
from game_service import game_service

front_office_service = front_office_football_service()

game_service = game_service()
game_service.get_offensive_play_personnel(1)

# print(front_office_service.get_roster())
# this is a flask application - run the below command to start as a localhost
    # flask --app flaskr run