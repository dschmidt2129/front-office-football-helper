import pandas as pd
import csv
import os
from player_service import player_service as ps
from team_service import team_service as ts
from PyQt5.QtWidgets import QApplication # this should allow the application to update real time
from coverage_assignments import (
    ManCoverageAssignment, Tampa2CoverageAssignment, Cover1Assignment,
    Cover2Assignment, Cover3SkyAssignment, Cover3CloudAssignment, Cover4Assignment, 
    Press1Assignment, Press2Assignment
)

class game_service:

    def __init__(self, path, output_widget):
        # initializing player_service and team_service
        self.ps = ps(path)
        self.ts = ts(path)
        self.cleaned_game_log = None  # Cache for the cleaned game log

    def get_game_log(self, file_name):
        # grabs the game log from the local game file system
        file = open(file_name)
        return file
    
    def read_game_log(self, path):
        # returns the file name from the local file system when retrieved from the game
        file = self.get_game_log(path + '/leagues/SFL00004/lastboxlog.html')
        return (file.name)
        
    def get_clean_game_result(self, path, output_widget): 
        # Create a new play data set instead of continuously iterating through the game log
        if self.cleaned_game_log is not None:
            return self.cleaned_game_log  # Return cached cleaned game log if it exists

        game_result = self.get_game_result(path, output_widget)
        game_result = game_result[0]
        play_counter = 0
        for game_index in game_result.loc[:,0]:
            play_result = game_result.loc[play_counter,0]
            play = play_result.split('OFFENSE')[0] # taking only the play result from the converted panda substring
            play_arr = play.split(' ')
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
               'two-point conversion' in play or # todo: need to figure out what to do with two-point conversion
               play_arr[3] == 'PENALTY:'):
                game_result.drop(index=play_counter, inplace=True)
                output_text = 'removing unwanted play : {}'.format(play)
                output_widget.append(output_text)
                QApplication.processEvents() # this should allow the application to update real time
            play_counter += 1
        game_result.reset_index(drop=True, inplace=True) # reset the index after dropping the unwanted plays
        self.cleaned_game_log = game_result  # Cache the cleaned game log
        return game_result
    
    def get_game_result(self, path, output_widget):
        game_log = self.get_game_log(self.read_game_log(path))
        all_tables = pd.read_html(game_log, keep_default_na=False)
        return all_tables
    
    def get_offensive_play_personnel(self,index, path):
        # Returns the offensive play personnel from the indexed play result from the game logs
        file = self.get_game_log(self.read_game_log(path))
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
    
    def get_defensive_play_personnel(self,index, path):
        # Returns the defensive play personnel from the indexed play result from the game logs
        file = self.get_game_log(self.read_game_log(path))
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

    def get_play_result(self,index, path, output_widget):
        # returns the play result from the game logs
        # Retrieve the play result from the cached cleaned game log
        if self.cleaned_game_log is None:
            self.get_clean_game_result(path, output_widget)  # Ensure the cleaned game log is initialized
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

    def get_player_performance_from_play(self, index, team_name, path, output_widget):
        # gets the player's performance and actions from the play +, -, etc...
        play_result = self.get_play_result(index, path, output_widget) 
        if play_result is None:
            output_text = f"Skipping play at index {index} due to missing play result."
            output_widget.append(output_text)
            QApplication.processEvents() # this should allow the application to update real time
            return None
        play_result_arr = play_result.split(' ')
        player_to_check_in_roster_first_name = (play_result_arr[3])

        player_to_check_in_roster_last_name = (play_result_arr[4])

        player_name = player_to_check_in_roster_first_name + ' ' + player_to_check_in_roster_last_name

        is_offense = self.ts.check_if_in_roster(player_name, team_name, path)
        output_text = str(play_result)
        output_widget.append(output_text)

        if(is_offense):
            offensive_play_personnel = self.get_offensive_play_personnel(index, path)
            output_text = f"Offensive play personnel at index {index}:"
            output_widget.append(output_text)
            QApplication.processEvents() # this should allow the application to update real time
            if offensive_play_personnel is not None and offensive_play_personnel.shape[0] > 0:
                formation = offensive_play_personnel.iloc[0,1]
                formation = str(formation)
                output_text = 'Formation : ' + formation
                output_widget.append(output_text)
                QApplication.processEvents() # this should allow the application to update real time
                offensive_play_personnel.drop(index=0, inplace=True)
                if 'pass' in play_result:
                    receivers_in_play = self.get_receivers_from_play(play_result, offensive_play_personnel, output_widget)
                    output_text = str(receivers_in_play)
                    output_widget.append(output_text)
                    QApplication.processEvents() # this should allow the application to update real time
                return offensive_play_personnel
            else:
                output_text = f"No offensive play personnel found at index {index}"
                output_widget.append(output_text)
                QApplication.processEvents() # this should allow the application to update real time
                return None
        else:          
            defensive_play_personnel = self.get_defensive_play_personnel(index, path)
            output_text = f"Defensive play personnel at index {index}:"
            output_widget.append(output_text)
            QApplication.processEvents() # this should allow the application to update real time
            if defensive_play_personnel is not None and defensive_play_personnel.shape[0] > 0:
                formation = defensive_play_personnel.iloc[0,1]
                formation = str(formation)
                output_text = 'Formation : ' + formation
                output_widget.append(output_text)
                QApplication.processEvents() # this should allow the application to update real time
                defensive_play_personnel.drop(index=0, inplace=True)
                if ('fell incomplete' in play_result or
                    'completed' in play_result or
                    'intercepted' in play_result
                    ):
                    offensive_play_personnel = self.get_offensive_play_personnel(index, path)                    
                    pass_defenders_in_play = self.get_pass_defenders_from_play(formation, play_result, defensive_play_personnel, output_widget, offensive_play_personnel)
                    output_text = str(pass_defenders_in_play)
                    output_widget.append(output_text)
                    QApplication.processEvents() # this should allow the application to update real time
                return defensive_play_personnel
            else:
                output_text = f"No defensive play personnel found at index {index}"
                output_widget.append(output_text)
                QApplication.processEvents() # this should allow the application to update real time
                return None
   
    def get_receivers_from_play(self, play_result, offensive_play_personnel, output_widget):
        receivers = []
        PENALTY_find = play_result.find("PENALTY")
        if(PENALTY_find != -1):
            play_result = play_result[:PENALTY_find]
        play_result_arr = play_result.split(' ')
        passer = play_result_arr[4]
        if 'fell incomplete' in play_result:
            caught = 0
            rec_yards = 0
            intended_receiver_last_name = (play_result_arr[12])
            intended_receiver_last_name = intended_receiver_last_name[:-1]
            yards_after_catch = 0
        elif 'was thrown incomplete' in play_result:
            caught = 0
            rec_yards = 0
            intended_receiver_last_name = (play_result_arr[13])
            intended_receiver_last_name = intended_receiver_last_name[:-1]
            yards_after_catch = 0
        elif 'completed' in play_result:
            intended_receiver_last_name = (play_result_arr[10])
        elif 'was blocked' in play_result:
            caught = 0
            rec_yards = 0
            yards_after_catch = 0
            intended_receiver_last_name = (play_result_arr[15])
            intended_receiver_last_name = intended_receiver_last_name[:-1]
        elif 'was dropped by' in play_result:
            caught = 0
            rec_yards = 0
            yards_after_catch = 0
            intended_receiver_last_name = (play_result_arr[11])
            intended_receiver_last_name = intended_receiver_last_name[:-1]
        elif 'intercepted' in play_result:
            caught = 0
            rec_yards = 0
            yards_after_catch = 0
            intended_receiver_last_name = (play_result_arr[11])
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
                        if 'after the catch' in play_result:
                            words = play_result.split()
                            index_after = words.index("after")
                            yards_after_catch = int(words[index_after - 2])
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
                new_rec_row.append(passer)
                receivers.append(new_rec_row)
        
        csv_file = 'receivers_in_game.csv'
        file_exists = os.path.isfile(csv_file)

        try:
            with open(csv_file, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                if not file_exists:
                    writer.writerow(['Player Name','Position' ,'Route Prioity', 'Route', 'Targeted?', 'Caught?', 'Yards', 'YAC', 'Passer'])
                writer.writerows(receivers)
                output_text = f"Receiver data for this play appended to '{csv_file}'."
                output_widget.append(output_text)
                QApplication.processEvents() # this should allow the application to update real time
        except Exception as e:
            output_text = f"Error writing to CSV file '{csv_file}': {e}"
            output_widget.append(output_text)
            QApplication.processEvents() # this should allow the application to update real time
        return receivers
    
    def get_coverage_assignment(self, route, position, off_formation, def_formation):
        # Dispatcher for coverage assignment classes
        if 'Man to Man' in def_formation:
            return ManCoverageAssignment(route, position, off_formation, def_formation)
        elif 'Tampa-2' in def_formation:
            return Tampa2CoverageAssignment(route, position, off_formation, def_formation)
        elif 'Cover-1' in def_formation:
            return Cover1Assignment(route, position, off_formation, def_formation)
        elif 'Cover-2' in def_formation:
            return Cover2Assignment(route, position, off_formation, def_formation)
        elif 'Cover-3 Sky' in def_formation:
            return Cover3SkyAssignment(route, position, off_formation, def_formation)
        elif 'Cover-3 Cloud' in def_formation:
            return Cover3CloudAssignment(route, position, off_formation, def_formation)
        elif 'Cover-4' in def_formation:
            return Cover4Assignment(route, position, off_formation, def_formation)
        elif 'Press-1' in def_formation:
            return Press1Assignment(route, position, off_formation, def_formation)
        elif 'Press-2' in def_formation:
            return Press2Assignment(route, position, off_formation, def_formation)
        else:
            return None
    
    def get_pass_defenders_from_play(self, formation, play_result, defensive_play_personnel, output_widget, offensive_play_personnel):     
        pass_def = []
        pass_defenders = []
        PENALTY_find = play_result.find("PENALTY")
        if(PENALTY_find != -1):
            play_result = play_result[:PENALTY_find]
        play_result_arr = play_result.split(' ')
        off_formation = offensive_play_personnel.iloc[0,1]
        off_formation = str(off_formation)
        def_formation = formation
        
        defensive_play_personnel.columns = ['Position_Player', 'Assignment', 'Rating']
        defensive_play_personnel[['Position', 'Player']] = defensive_play_personnel['Position_Player'].str.split(' ', n=1, expand=True)
        defensive_play_personnel = defensive_play_personnel.drop(columns=['Position_Player'])
        defensive_play_personnel = defensive_play_personnel[['Position', 'Player', 'Assignment', 'Rating']]
        
        Num_TE = 0
        Num_Slot = 0
        
        if 'fell incomplete' in play_result:
            intended_receiver_last_name = (play_result_arr[12])
            intended_receiver_last_name = intended_receiver_last_name[:-1]            
        elif 'completed' in play_result:
            intended_receiver_last_name = (play_result_arr[10])
        elif 'intercepted' in play_result:
            intended_receiver_last_name = (play_result_arr[11])
            
        for i in range(1,6):
            if ('Primary' in str(offensive_play_personnel.iloc[i, 1]) or
                'Secondary' in str(offensive_play_personnel.iloc[i, 1]) or
                'Outlet' in str(offensive_play_personnel.iloc[i, 1])
            ):
                receiver_name_and_position = str(offensive_play_personnel.iloc[i, 0])
                position_and_name = receiver_name_and_position.split(' ', 1)
                receiver_name = position_and_name[1]
                position = position_and_name[0]
                match position:
                    case 'SLOT':
                        Num_Slot += 1
                        match Num_Slot:
                            case 1:
                                position = 'R'
                            case 2:
                                position = 'S'
                            case 3:
                                position = 'V'
                    case 'TE':
                        Num_TE += 1
                        match Num_TE:
                            case 1:
                                position = 'Y'
                            case 2:
                                position = 'T'
                            case 3:
                                position = 'U'
                if receiver_name.endswith(intended_receiver_last_name):
                    priority_plus_route = str(offensive_play_personnel.iloc[i, 1])
                    priority_plus_route_arr = priority_plus_route.split(',')
                    route = priority_plus_route_arr[1]
                    route = route.lstrip()
                    
                    assignment_class = self.get_coverage_assignment(route, position, off_formation, def_formation)
                    if assignment_class:
                        prim_assigned, doub_assigned = assignment_class.assign()
                    else:
                        prim_assigned, doub_assigned = None, None                 
                    prim_def_name = ''
                    doub_def_name = ''

                    if prim_assigned:
                        defender_row = defensive_play_personnel[defensive_play_personnel['Position'] == prim_assigned]
                        if not defender_row.empty:
                            prim_def_name = defender_row['Player'].iloc[0]

                    if doub_assigned:
                        defender_row = defensive_play_personnel[defensive_play_personnel['Position'] == doub_assigned]
                        if not defender_row.empty:
                            doub_def_name = defender_row['Player'].iloc[0]
                    
                    pass_def.append(receiver_name)
                    pass_def.append(prim_def_name)
                    pass_def.append(doub_def_name)
                    pass_defenders.append(pass_def)

        csv_file = 'pass_def_in_game.csv'
        file_exists = os.path.isfile(csv_file)

        try:
            with open(csv_file, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                if not file_exists:
                    writer.writerow(['Receiver', 'Primary Defender', 'Double Team'])
                writer.writerows(pass_defenders)
                output_text = f"Pass defense data for this play appended to '{csv_file}'."
                output_widget.append(output_text)
                QApplication.processEvents()
        except Exception as e:
            output_text = f"Error writing to CSV file '{csv_file}': {e}"
            output_widget.append(output_text)
            QApplication.processEvents()
        return pass_defenders
