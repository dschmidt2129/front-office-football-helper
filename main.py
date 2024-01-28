from front_office_football_service import front_office_football_service
from team_service import team_service

front_office_service = front_office_football_service()

team_services = team_service()
# (service.get_player_name_from_play())
team_services.get_team_info('Cleveland')
