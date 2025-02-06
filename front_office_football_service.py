import pandas as pd
from team_service import team_service as ts
from player_service import player_service as ps
from game_service import game_service as gs

class front_office_football_service:
    def __init__(self):
        self.gs = gs()

    def write_gamelog_to_csv(self):
        # write the game log to a csv file
        # get the game log
        play_results = self.gs.get_game_result()
        play_counter = 0
        for i in range(1, len(play_results)):
            print(self.gs.get_player_performance_from_play(play_counter, 'Las Vegas'))
            play_counter += 1
        # player_performance = gs.get_player_performance_from_play(1, 'Las Vegas')
        return
