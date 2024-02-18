import pandas as pd
from team_service import team_service as team_services
from player_service import player_service as player_services
from game_service import game_service as game_services

class front_office_football_service:
    def __init__(self):
        # no variables need initialized
        pass

    def get_roster(self):
        # retrieves the roster from the game logs so that the stats can be compiled
        # should read from player_record.csv and find the matching player and team ids from another file
        # can match player id with the id in player_information.csv
        # can match team id with the id in team_information.csv
        return
