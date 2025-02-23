from game_service import game_service as gs

class front_office_football_service:
    def __init__(self):
        self.gs = gs()

    def write_gamelog_to_csv(self):
        # write the game log to a csv file
        # get the game log
        play_results = self.gs.get_clean_game_result()
        # print(f'play results : {play_results}')
        play_counter = 0
        for play_result in play_results:
            try:
                # this is not iterating through the entire game log
                print(f"Processing play {play_counter}")
                player_performance = self.gs.get_player_performance_from_play(play_counter, 'Las Vegas')
                print(player_performance)
                play_counter += 1
            except IndexError as e:
                print(f"IndexError: {e} at play {play_counter}")
        return
