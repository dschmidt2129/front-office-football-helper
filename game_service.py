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
    
    def get_offensive_play_personnel(self,index):
        # returns the offensive play personnel from the indexed play result from the game logs
        file = self.get_game_log(self.read_game_log())
        all_tables = pd.read_html(file, keep_default_na=False)
        # the first play always starts at index 3
        offensive_plays = all_tables[index].iloc[:,0:3]
        # print(offensive_plays)
        return offensive_plays
    
    def get_defensive_play_personnel(self,index):
        # returns the defensive play personnel from the indexed play result from the game logs
        file = self.get_game_log(self.read_game_log())
        all_tables = pd.read_html(file, keep_default_na=False)
        # the first play always starts at index 3
        defensive_plays = all_tables[index].iloc[:,3:6]
        # print(defensive_plays)
        return defensive_plays

    def get_play_result(self,index):
        # returns the play result from the game logs
        file = self.get_game_log(self.read_game_log())
        # index 0 is a list of the all of the play results
        all_tables = pd.read_html(file, keep_default_na=False)
        plays = all_tables[0] # currently a dataframe with one column
        play_result = plays.loc[index+3,0] # for whatever reason, the html table isn't indexed like an array or list when converted to a dataframe
        play_result = play_result.split('OFFENSE')[0] # taking only the play result from the converted panda substring
        # print(play_result)
        return play_result

    def get_player_performance_from_play(self, index, team_name):
        # todo: iterate through the game log and get the player's performance and actions from the play +, -, etc... and write to csv 
        # gets the player's performance and actions from the play +, -, etc...
        play_result = self.get_play_result(index) 
        play_result_arr = play_result.split(' ')
        player_to_check_in_roster_first_name = (play_result_arr[3])
        # print('Player First Name: ' + player_to_check_in_roster_first_name)
        player_to_check_in_roster_last_name = (play_result_arr[4])
        # print('Player Last Name: ' + player_to_check_in_roster_last_name)
        player_name = player_to_check_in_roster_first_name + ' ' + player_to_check_in_roster_last_name
        # print('Player Name: ' + player_name)
        is_offense = self.ts.check_if_in_roster(player_name, team_name)
        print(play_result)
        # print('Is Offense? : ' + str(is_offense))
        player_index = 0
        if(is_offense):
            offensive_play_personnel = self.get_offensive_play_personnel(index)
            # print(offensive_play_personnel)
            # quarterback and offensive line are special cases where they don't have a play result and qb will return *** instead of +,-
            formation = offensive_play_personnel.iloc[0]
            offensive_play_personnel.drop(index=0, inplace=True)
            print('Formation : ' + formation)
            for player in offensive_play_personnel[offensive_play_personnel.columns[0]]:
                player = offensive_play_personnel.iloc[player_index]
                player_index += 1
                print(player)
            # player = offensive_play_personnel.iloc[player_index]
            # print(player)
            return offensive_play_personnel
        else:
           defensive_play_personnel = self.get_defensive_play_personnel(index)
        #    print(defensive_play_personnel)
           formation = defensive_play_personnel.iloc[0]
           print('Formation : ' + formation)
           defensive_play_personnel.drop(index=0, inplace=True)
           for player in defensive_play_personnel[defensive_play_personnel.columns[0]]:
               player = defensive_play_personnel.iloc[player_index]
               print(player)
               player_index += 1
        #    player = defensive_play_personnel.iloc[player_index]
        #    print(player)
           return defensive_play_personnel