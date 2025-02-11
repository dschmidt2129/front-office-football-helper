from front_office_football_service import front_office_football_service
from team_service import team_service
from game_service import game_service
from player_service import player_service

front_office_service = front_office_football_service()
 # todo: need to update this program to include up to date roster and gamelog
game_service = game_service()
front_office_football_service = front_office_football_service()
front_office_football_service.write_gamelog_to_csv()
# player_service = player_service()
# team_service = team_service()

# this is a flask application - run the below command to start as a localhost
    # flask --app flaskr run