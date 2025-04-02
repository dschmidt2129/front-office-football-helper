from game_service import game_service as gs

class front_office_football_service:
    def __init__(self):
        self.gs = gs()

    def iterate_through_gamelog(self):
        # write the game log to a csv file
        # get the game log
        play_results = self.gs.get_clean_game_result()
        # print(f'play results : {play_results}')
        play_counter = 0
        # Iterate through all plays in the cleaned game log
        while play_counter < len(play_results):
            try:
                print(f"Processing play {play_counter}")
                # Get player performance for the current play
                player_performance = self.gs.get_player_performance_from_play(play_counter, 'Las Vegas')
                print(player_performance)
                play_counter += 1  # Move to the next play
            except IndexError as e:
                print(f"IndexError: {e} at play {play_counter}")
                play_counter += 1  # Skip the problematic play and continue
            except Exception as e:
                print(f"Unexpected error: {e} at play {play_counter}")
                play_counter += 1  # Skip the problematic play and continue
        print("Finished processing all plays.")
        return
