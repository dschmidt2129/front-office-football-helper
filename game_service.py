import pandas as pd
from player_service import player_service as ps
from team_service import team_service as ts

class game_service:

    def __init__(self):
        # initializing player_service and team_service
        self.ps = ps()
        self.ts = ts()
        pass

    def get_game_log(self, file_name):
        # grabs the game log from the local game file system
        file = open(file_name)
        return file
    
    def read_game_log(self):
        # returns the file name from the local file system when retrieved from the game
        file = self.get_game_log('resources/lastboxlog.html')
        return (file.name)
    
    def get_game_result(self):
        game_log = self.get_game_log(self.read_game_log())
        all_tables = pd.read_html(game_log, keep_default_na=False)
        return all_tables
    
    def get_offensive_play_personnel(self,index):
        # returns the offensive play personnel from the indexed play result from the game logs
        file = self.get_game_log(self.read_game_log())
        all_tables = pd.read_html(file, keep_default_na=False)
        offensive_plays = all_tables[index].iloc[:,0:3]
        print(f"Offensive plays at index {index}:")
        return offensive_plays
    
    def get_defensive_play_personnel(self,index):
        # returns the defensive play personnel from the indexed play result from the game logs
        file = self.get_game_log(self.read_game_log())
        all_tables = pd.read_html(file, keep_default_na=False)
        defensive_plays = all_tables[index].iloc[:,3:6]
        print(f"Defensive plays at index {index}:")
        return defensive_plays

    def get_play_result(self,index):
        # returns the play result from the game logs
        file = self.get_game_log(self.read_game_log())
        # index 0 is a list of the all of the play results
        all_tables = pd.read_html(file, keep_default_na=False)
        plays = all_tables[0] # currently a dataframe with one column
        play_result = plays.loc[index,0]
        play_result = play_result.split('OFFENSE')[0] # taking only the play result from the converted panda substring
        print(f"Plays DataFrame at index {index}:")
        if('Played in ' in play_result or
           'won the toss and elected to' in play_result or
           'Start of first quarter' in play_result):
            return 'Played in location logs, skipping...'
        elif('Play-Action' in play_result):
            play_result = play_result.replace('Play-Action. ', '')
            return play_result
        elif('Final Score' in play_result):
            return 'Final Score'
        return play_result

    def get_player_performance_from_play(self, index, team_name):
        # gets the player's performance and actions from the play +, -, etc...
        index -= 3 # this is to account for the play result being 3 plays ahead of the play personnel
        play_result = self.get_play_result(index) 
        match play_result:
            case str() if 'kicked' in play_result:
                return 'kickoff or field goal play, skipping...'
            case str() if 'punted' in play_result:
                return 'punt play, skipping...'
            case str() if 'attempted' in play_result:
                return 'attempted field goal or extra point play, skipping...'
            case str() if 'PENALTY' in play_result:
                return 'penalty play, skipping...'
            case str() if 'quarter' in play_result:
                return 'start of or end of quarter, skipping...'
            case str() if 'End of' in play_result:
                return 'end of game, skipping...'
            case str() if 'two-minute' in play_result:
                return 'two-minute warning, skipping...'
            case str() if 'time out' in play_result:
                return 'time out play, skipping...'
            case str() if 'Extra point' in play_result:
                return 'extra point play, skipping...'
            case str() if 'Played in location' in play_result:
                return 'Played in location logs, skipping...'
            
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