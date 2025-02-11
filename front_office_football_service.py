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
        play_counter = 3
        for play_result in play_results:
            if('Final Score' in play_result):
                break
            try:
                print(f"Processing play {play_counter}")
                player_performance = self.gs.get_player_performance_from_play(play_counter, 'Las Vegas')
                print(player_performance)
                play_counter += 1
            except IndexError as e:
                print(f"IndexError: {e} at play {play_counter}")
        return
