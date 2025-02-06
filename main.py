from front_office_football_service import front_office_football_service
from team_service import team_service
from game_service import game_service
from player_service import player_service

front_office_service = front_office_football_service()

game_service = game_service()
# game_service.get_player_performance_from_play(1, 'Las Vegas')
front_office_football_service = front_office_football_service()
front_office_football_service.write_gamelog_to_csv()
# player_service = player_service()
# player_service.get_player_team_id(player_service.get_player_id('Baker Mayfield'))
# team_service = team_service()
# team_service.check_if_in_roster('Baker Mayfield', 'Indianapolis')

# this is a flask application - run the below command to start as a localhost
    # flask --app flaskr run