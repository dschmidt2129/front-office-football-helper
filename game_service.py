import pandas as pd
from player_service import player_service as ps
from team_service import team_service as ts

class game_service:

    def __init__(self):
        # initializing player_service and team_service
        self.ps = ps()
        self.ts = ts()
        self.cleaned_game_log = None  # Cache for the cleaned game log

    def get_game_log(self, file_name):
        # grabs the game log from the local game file system
        file = open(file_name)
        return file
    
    def read_game_log(self):
        # returns the file name from the local file system when retrieved from the game
        file = self.get_game_log('resources/lastboxlog.html')
        return (file.name)
        
    def get_clean_game_result(self): 
        # Create a new play data set instead of continuously iterating through the game log
        if self.cleaned_game_log is not None:
            return self.cleaned_game_log  # Return cached cleaned game log if it exists

        game_result = self.get_game_result()
        game_result = game_result[0]
        play_counter = 0
        for game_index in game_result.loc[:,0]:
            play_result = game_result.loc[play_counter,0]
            play = play_result.split('OFFENSE')[0] # taking only the play result from the converted panda substring
            if('kicked' in play or
               'punted' in play or
               'attempted' in play or
               'Start of' in play or
               'End of' in play or
               'two-minute' in play or
               'time out' in play or
               'Extra point' in play or
               'Played in' in play or
               'won the toss' in play or
               'Final Score' in play):
                game_result.drop(index=play_counter, inplace=True)
                print('removing unwanted play : {}'.format(play))
            play_counter += 1
        game_result.reset_index(drop=True, inplace=True) # reset the index after dropping the unwanted plays
        self.cleaned_game_log = game_result  # Cache the cleaned game log
        return game_result
    
    def get_game_result(self):
        game_log = self.get_game_log(self.read_game_log())
        all_tables = pd.read_html(game_log, keep_default_na=False)
        return all_tables
    
    def get_offensive_play_personnel(self,index):
        # returns the offensive play personnel from the indexed play result from the game logs
        index += 1
        file = self.get_game_log(self.read_game_log())
        all_tables = pd.read_html(file, keep_default_na=False)
        offensive_plays = all_tables[index].iloc[:,0:3]
        # print(f"Offensive plays at index {index}:")
        return offensive_plays
    
    def get_defensive_play_personnel(self,index):
        index += 1
        # returns the defensive play personnel from the indexed play result from the game logs
        file = self.get_game_log(self.read_game_log())
        all_tables = pd.read_html(file, keep_default_na=False)
        defensive_plays = all_tables[index].iloc[:,3:6]
        # print(f"Defensive plays at index {index}:")
        return defensive_plays

    def get_play_result(self,index):
        # returns the play result from the game logs
        # Retrieve the play result from the cached cleaned game log
        if self.cleaned_game_log is None:
            self.get_clean_game_result()  # Ensure the cleaned game log is initialized
        try:
        # print(f"Play result at index {index}:")
            play_result = self.cleaned_game_log.loc[index,0]
            play_result = play_result.split('OFFENSE')[0] # taking only the play result from the converted panda substring
            if('Play-Action' in play_result):
                play_result = play_result.replace('Play-Action. ', '')
            return play_result
        except KeyError:
            print(f"Index {index} is out of bounds for the cleaned game log.")
            return None

    def get_player_performance_from_play(self, index, team_name):
        # gets the player's performance and actions from the play +, -, etc...
        play_result = self.get_play_result(index) 
            
        play_result_arr = play_result.split(' ')
        player_to_check_in_roster_first_name = (play_result_arr[3])

        player_to_check_in_roster_last_name = (play_result_arr[4])

        player_name = player_to_check_in_roster_first_name + ' ' + player_to_check_in_roster_last_name

        is_offense = self.ts.check_if_in_roster(player_name, team_name)
        print(play_result)

        if(is_offense):
            offensive_play_personnel = self.get_offensive_play_personnel(index)
            print(f"Offensive play personnel at index {index}:")
            if offensive_play_personnel.shape[0] > 0:
                formation = offensive_play_personnel.iloc[0,1]
                formation = str(formation)
                print('Formation : ' + formation)
                offensive_play_personnel.drop(index=0, inplace=True)
                return offensive_play_personnel
            else:
                print(f"No offensive play personnel found at index {index}")
                return None
        else:
            defensive_play_personnel = self.get_defensive_play_personnel(index)
            print(f"Defensive play personnel at index {index}:")
            if defensive_play_personnel.shape[0] > 0:
                formation = defensive_play_personnel.iloc[0,1]
                formation = str(formation)
                print('Formation : ' + formation)
                defensive_play_personnel.drop(index=0, inplace=True)
                return defensive_play_personnel
            else:
                print(f"No defensive play personnel found at index {index}")
                return None