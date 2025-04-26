import pandas as pd
import csv
import os
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
               'Final Score' in play or
               'False Start' in play or
               'Informal' in play or
               'dropped to one knee' in play or
               # 'PENALTY' in play or  # to do:  is this what we want?  If we don't remove penalty plays then parsing becomes difficult for (at least) YAC identification
               'two-point conversion' in play): # todo: need to figure out what to do with two-point conversion
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
        # Returns the offensive play personnel from the indexed play result from the game logs
        file = self.get_game_log(self.read_game_log())
        all_tables = pd.read_html(file, keep_default_na=False)

        # Ensure the index matches the cleaned game log
        try:
            offensive_plays = all_tables[index + 1].iloc[:, 0:3]  # Adjust index to match personnel table
            # print(f"Offensive plays at index {index + 1}:")
            # print(offensive_plays)
            return offensive_plays
        except IndexError:
            print(f"No offensive play personnel found for index {index + 1}")
            return None
    
    def get_defensive_play_personnel(self,index):
        # Returns the defensive play personnel from the indexed play result from the game logs
        file = self.get_game_log(self.read_game_log())
        all_tables = pd.read_html(file, keep_default_na=False)

        # Ensure the index matches the cleaned game log
        try:
            defensive_plays = all_tables[index + 1].iloc[:, 3:6]  # Adjust index to match personnel table
            # print(f"Defensive plays at index {index + 1}:")
            # print(defensive_plays)
            return defensive_plays
        except IndexError:
            print(f"No defensive play personnel found for index {index + 1}")
            return None

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
        if play_result is None:
            print(f"Skipping play at index {index} due to missing play result.")
            return None
        play_result_arr = play_result.split(' ')
        player_to_check_in_roster_first_name = (play_result_arr[3])

        player_to_check_in_roster_last_name = (play_result_arr[4])

        player_name = player_to_check_in_roster_first_name + ' ' + player_to_check_in_roster_last_name

        is_offense = self.ts.check_if_in_roster(player_name, team_name)
        print(play_result)

        if(is_offense):
            offensive_play_personnel = self.get_offensive_play_personnel(index)
            print(f"Offensive play personnel at index {index}:")
            if offensive_play_personnel is not None and offensive_play_personnel.shape[0] > 0:
                formation = offensive_play_personnel.iloc[0,1]
                formation = str(formation)
                print('Formation : ' + formation)
                offensive_play_personnel.drop(index=0, inplace=True)
                if 'pass' in play_result:
                    receivers_in_play = self.get_receivers(play_result, offensive_play_personnel)
                    print(receivers_in_play)
            else:
                print(f"No offensive play personnel found at index {index}")
                return None
        else:
            defensive_play_personnel = self.get_defensive_play_personnel(index)
            print(f"Defensive play personnel at index {index}:")
            if defensive_play_personnel is not None and defensive_play_personnel.shape[0] > 0:
                formation = defensive_play_personnel.iloc[0,1]
                formation = str(formation)
                print('Formation : ' + formation)
                defensive_play_personnel.drop(index=0, inplace=True)
                return defensive_play_personnel
            else:
                print(f"No defensive play personnel found at index {index}")
                return None
   
    def get_receivers(self, play_result, offensive_play_personnel):
        receivers = []
        play_result_arr = play_result.split(' ')
        if 'incomplete' in play_result:  # to do:  need to add case for intercetions
            caught = 0
            rec_yards = 0
            intended_receiver_last_name = (play_result_arr[12])
            intended_receiver_last_name = intended_receiver_last_name[:-1]
            yards_after_catch = 0
        elif 'completed' in play_result:
            intended_receiver_last_name = (play_result_arr[10])
            # caught = 1
            # rec_yards = int(play_result_arr[12])
            # yards_after_catch = 0
            # if 'after the catch' in play_result:  # to do - resolve parsing YAC on plays where a penalty was called but not accepted
            #     last_index = len(play_result_arr) - 1    
            #     yards_after_catch = int(play_result_arr[last_index-5])
        elif 'was blocked' in play_result:
            caught = 0
            rec_yards = 0
            yards_after_catch = 0
            intended_receiver_last_name = (play_result_arr[15])
            intended_receiver_last_name = intended_receiver_last_name[:-1]
        for i in range(1,6):
            if ('Primary' in str(offensive_play_personnel.iloc[i, 1]) or
                'Secondary' in str(offensive_play_personnel.iloc[i, 1]) or
                'Outlet' in str(offensive_play_personnel.iloc[i, 1])
            ):
                receiver_name_and_position = str(offensive_play_personnel.iloc[i, 0])
                position_and_name = receiver_name_and_position.split(' ', 1)
                receiver_name = position_and_name[1]
                position = position_and_name[0]
                priority_plus_route = str(offensive_play_personnel.iloc[i, 1])
                priority_plus_route_arr = priority_plus_route.split(',')
                priority = priority_plus_route_arr[0]
                route = priority_plus_route_arr[1]
                route = route.lstrip()
                if receiver_name.endswith(intended_receiver_last_name):
                    targeted = 1
                    if 'completed' in play_result:
                        caught = 1
                        rec_yards = int(play_result_arr[12])
                        yards_after_catch = 0
                        if 'after the catch' in play_result:  # to do - resolve parsing YAC on plays where a penalty was called but not accepted
                            last_index = len(play_result_arr) - 1    
                            yards_after_catch = int(play_result_arr[last_index-5])
                else:
                    targeted = 0
                    caught = 0
                    rec_yards = 0
                    yards_after_catch = 0
                new_rec_row = []
                new_rec_row.append(receiver_name)
                new_rec_row.append(position)
                new_rec_row.append(priority)
                new_rec_row.append(route)
                new_rec_row.append(targeted)
                new_rec_row.append(caught)
                new_rec_row.append(rec_yards)
                new_rec_row.append(yards_after_catch)
                receivers.append(new_rec_row)
        
        csv_file = 'receivers_in_game.csv'
        file_exists = os.path.isfile(csv_file)

        try:
            with open(csv_file, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                if not file_exists:
                    writer.writerow(['Player Name','Position' ,'Route Prioity', 'Route', 'Targeted?', 'Caught?', 'Yards', 'YAC'])
                writer.writerows(receivers)
                print(f"Receiver data for this play appended to '{csv_file}'.")
        except Exception as e:
            print(f"Error writing to CSV file '{csv_file}': {e}")
        return receivers