from game_service import game_service as gs
from PyQt5.QtWidgets import QApplication

class front_office_football_service:
    def __init__(self, path, output_widget):
        self.gs = gs(path, output_widget)

    def iterate_through_gamelog(self, path, combo_box, team_index, team_city, output_widget):
        # write the game log to a csv file
        # get the game log
        play_results = self.gs.get_clean_game_result(path, output_widget)
        # print(f'play results : {play_results}')
        play_counter = 0
        # Iterate through all plays in the cleaned game log
        while play_counter < len(play_results):
            try:
                output_text = f"Processing play {play_counter}"
                output_widget.append(output_text)
                # Get player performance for the current play
                player_performance = self.gs.get_player_performance_from_play(play_counter, team_city, path, output_widget)
                output_text = str(player_performance)
                output_widget.append(output_text)
                QApplication.processEvents() # this should allow the application to update real time
                play_counter += 1  # Move to the next play
            # todo: account for final score or end of the list
            except IndexError as e:
                output_text = f"IndexError: {e} at play {play_counter}"
                output_widget.append(output_text)
                QApplication.processEvents() # this should allow the application to update real time
                play_counter += 1  # Skip the problematic play and continue
            except Exception as e:
                output_text = f"Unexpected error: {e} at play {play_counter}"
                output_widget.append(output_text)
                QApplication.processEvents() # this should allow the application to update real time
                play_counter += 1  # Skip the problematic play and continue
            self.gs.finalize_receiver_outputs(output_widget)
        output_text = "Finished processing all plays."
        output_widget.append(output_text)
        return
