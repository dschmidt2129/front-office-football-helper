import pandas as pd
import csv
import os
from player_service import player_service as ps
from team_service import team_service as ts

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
            if offensive_play_personnel is not None and offensive_play_personnel.shape[0] > 0:
                formation = offensive_play_personnel.iloc[0,1]
                formation = str(formation)
                output_text = 'Formation : ' + formation
                output_widget.append(output_text)
                offensive_play_personnel.drop(index=0, inplace=True)
                if 'pass' in play_result:
                    receivers_in_play = self.get_receivers_from_play(play_result, offensive_play_personnel, output_widget)
                    output_text = str(receivers_in_play)
                    output_widget.append(output_text)
                return offensive_play_personnel
            else:
                output_text = f"No offensive play personnel found at index {index}"
                output_widget.append(output_text)
                return None
        else:          
            defensive_play_personnel = self.get_defensive_play_personnel(index, path)
            output_text = f"Defensive play personnel at index {index}:"
            output_widget.append(output_text)
            if defensive_play_personnel is not None and defensive_play_personnel.shape[0] > 0:
                formation = defensive_play_personnel.iloc[0,1]
                formation = str(formation)
                output_text = 'Formation : ' + formation
                output_widget.append(output_text)
                defensive_play_personnel.drop(index=0, inplace=True)
                if ('fell incomplete' in play_result or
                    'completed' in play_result or
                    'intercepted' in play_result
                    ):
                    offensive_play_personnel = self.get_offensive_play_personnel(index, path)                    
                    pass_defenders_in_play = self.get_pass_defenders_from_play(formation, play_result, defensive_play_personnel, output_widget, offensive_play_personnel)
                    output_text = str(pass_defenders_in_play)
                    output_widget.append(output_text)
                return defensive_play_personnel
            else:
                output_text = f"No defensive play personnel found at index {index}"
                output_widget.append(output_text)
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
        except Exception as e:
            output_text = f"Error writing to CSV file '{csv_file}': {e}"
            output_widget.append(output_text)
        return receivers
    
    def get_pass_defenders_from_play(self, formation, play_result, defensive_play_personnel, output_widget, offensive_play_personnel):     
        pass_defenders = []
        PENALTY_find = play_result.find("PENALTY")
        if(PENALTY_find != -1):
            play_result = play_result[:PENALTY_find]
        play_result_arr = play_result.split(' ')
        off_formation = offensive_play_personnel.iloc[0,1]
        off_formation = str(off_formation)
        def_formation = formation
        
        # The first column after the index (which is column 1 in a 0-indexed DataFrame)
        # contains the position like 'LDE', 'NT', 'LCB', etc.
        
        defensive_play_personnel.columns = ['Position_Player', 'Assignment', 'Rating']
        
        # Let's clean up the 'Position_Player' column to separate position and player name
        defensive_play_personnel[['Position', 'Player']] = defensive_play_personnel['Position_Player'].str.split(' ', n=1, expand=True)
        defensive_play_personnel = defensive_play_personnel.drop(columns=['Position_Player'])
        
        # Reorder columns for better readability (optional)
        defensive_play_personnel = defensive_play_personnel[['Position', 'Player', 'Assignment', 'Rating']]
        
        print("Original DataFrame (after some initial cleaning for clarity):")
        print(defensive_play_personnel)
        print("\n" + "="*30 + "\n") # prints 30 equal signs for separation
        
        Num_TE = 0
        Num_Slot = 0
        prim_assigned = ''
        prim_coverage_type = ''
        prim_defender = ''
        prim_def_name = ''
        doub_assigned = ''
        doub_coverage_type = ''
        doub_defender = ''
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
                # todo: convert if statements to match cases for better speed and readability
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
                    
                    if (position == 'X(SE)' or
                        (position == 'Z(FL)' and '131' in off_formation) or
                        (position == 'T' and '221' in off_formation) or
                        (position == 'T' and '230' in off_formation)
                        ):
                        if ('Man to Man' in def_formation or
                            'Cover-2' in def_formation or
                            'Cover-1' in def_formation or
                            'Cover-3 Cloud' in def_formation or
                            'Press-2' in def_formation or
                            'Press-1' in def_formation or
                            'Tampa-2' in def_formation
                            ):
                            prim_assigned = 'LCB'  
                        elif ('Cover-3 Sky' in def_formation):
                            match route:
                                case 'S Screen (S)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'WLB'
                                    else:
                                        prim_assigned = 'LCB'
                                case 'F Flat (0-4)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'WLB'
                                    else:
                                        prim_assigned = 'LCB'
                                case '0 Dig (0-4)':
                                    if ('43' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'MLB'                                        
                                        elif('Nickel' in def_formation):
                                            prim_assigned = 'WLB'                                        
                                        else:
                                            prim_assigned = 'MLB'                                    
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'WLB'                                        
                                        elif('Nickel' in def_formation):
                                            prim_assigned = 'WLB'                                        
                                        else:
                                            prim_assigned = 'WILB'
                                case '1 Out (5-8)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'WLB'
                                    else:
                                        prim_assigned = 'LCB'
                                case '2 Slant (5-8)':
                                    if ('43' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'MLB'                                        
                                        elif('Nickel' in def_formation):
                                            prim_assigned = 'WLB'                                        
                                        else:
                                            prim_assigned = 'MLB'                                    
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'WLB'                                        
                                        elif('Nickel' in def_formation):
                                            prim_assigned = 'WLB'                                        
                                        else:
                                            prim_assigned = 'WILB'
                                case '3 Comeback (9-12)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'WLB'                                    
                                    else:
                                        prim_assigned = 'LCB'
                                case '4 Curl (9-12)':
                                    if ('43' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'MLB'                                        
                                        elif('Nickel' in def_formation):
                                            prim_assigned = 'WLB'                                        
                                        else:
                                            prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'WLB'                                        
                                        elif('Nickel' in def_formation):
                                            prim_assigned = 'WLB'                                        
                                        else:
                                            prim_assigned = 'WILB'
                                case '5 Deep Out (13-18)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'LCB'
                                    else:
                                        prim_assigned = 'NB'
                                case '6 Deep In (13-18)':
                                    prim_assigned = 'FS'
                                case '7 Corner (19-26)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'LCB'
                                    else:
                                        prim_assigned = 'NB'
                                case '8 Post (19-26)':
                                    prim_assigned = 'FS'
                                case '9 Fade (27-39)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'LCB'
                                    else:
                                        prim_assigned = 'NB'
                                case 'W Wheel (9-18)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'LCB'
                                    else:
                                        prim_assigned = 'NB'
                                case 'D Deep Fade (40+)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'LCB'
                                    else:
                                        prim_assigned = 'NB'                                                                      
                        elif ('Cover-4' in def_formation):
                            match route:
                                case 'S Screen (S)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'WLB'
                                    else:
                                        prim_assigned = 'LCB'
                                case 'F Flat (0-4)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'WLB'
                                    else:
                                        prim_assigned = 'LCB'
                                case '0 Dig (0-4)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                            prim_assigned = 'SILB'
                                        elif('Dime Personnel' in def_formation):
                                            prim_assigned = 'SLB'
                                case '1 Out (5-8)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'WLB'
                                    else:
                                        prim_assigned = 'LCB'
                                case '2 Slant (5-8)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                            prim_assigned = 'SILB'
                                        elif('Dime Personnel' in def_formation):
                                            prim_assigned = 'SLB'
                                case '3 Comeback (9-12)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'WLB'
                                    else:
                                        prim_assigned = 'LCB'
                                case '4 Curl (9-12)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                            prim_assigned = 'SILB'
                                        elif('Dime Personnel' in def_formation):
                                            prim_assigned = 'SLB'
                                case '5 Deep Out (13-18)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'LCB'
                                    elif('Nickel Personnel' in def_formation or'Dime Personnel' in def_formation):
                                        prim_assigned = 'NB'
                                case '6 Deep In (13-18)':
                                    prim_assigned = 'FS'
                                case '7 Corner (19-26)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'LCB'
                                    elif('Nickel Personnel' in def_formation or'Dime Personnel' in def_formation):
                                        prim_assigned = 'NB'
                                case '8 Post (19-26)':
                                    prim_assigned = 'FS'
                                case '9 Fade (27-39)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'LCB'
                                    elif('Nickel Personnel' in def_formation or'Dime Personnel' in def_formation):
                                        prim_assigned = 'NB'
                                case 'W Wheel (9-18)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'WLB'
                                    elif('Nickel Personnel' in def_formation or'Dime Personnel' in def_formation):
                                        prim_assigned = 'LCB'
                                case 'D Deep Fade (40+)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'LCB'
                                    elif('Nickel Personnel' in def_formation or'Dime Personnel' in def_formation):
                                        prim_assigned = 'NB'
                    
                    elif (position == 'Z(FL)' or position == 'U'):
                        if ('Man to Man' in def_formation or
                            'Cover-2' in def_formation or
                            'Cover-1' in def_formation or                            
                            'Press-2' in def_formation or
                            'Press-1' in def_formation or
                            'Tampa-2' in def_formation
                            ):
                            prim_assigned = 'RCB'                            
                        elif ('Cover-3 Cloud' in def_formation):
                            match route:
                                case 'S Screen (S)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                case 'F Flat (0-4)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                case '0 Dig (0-4)':
                                    if ('Regular' in def_formation):
                                        if ('43' in def_formation):
                                            prim_assigned = 'MLB'
                                        elif ('34' in def_formation):
                                            prim_assigned = 'SILB'
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'                                    
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'NB'                            
                                        else:
                                            prim_assigned = 'SILB'
                                case '1 Out (5-8)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                case '2 Slant (5-8)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'                                    
                                    elif ('34' in def_formation):
                                        if ('Nickel' in def_formation or 'Dime' in def_formation):
                                            prim_assigned = 'SLB'                            
                                        else:
                                            prim_assigned = 'SILB'
                                case '3 Comeback (9-12)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                case '4 Curl (9-12)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'                                    
                                    elif ('34' in def_formation):
                                        if ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                            prim_assigned = 'SLB'                            
                                        else:
                                            prim_assigned = 'SILB'
                                case '5 Deep Out (13-18)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'RCB'
                                    else:
                                        prim_assigned = 'SS'
                                case '6 Deep In (13-18)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SS'
                                    else:
                                        prim_assigned = 'FS'
                                case '7 Corner (19-26)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'RCB'
                                    else:
                                        prim_assigned = 'SS'
                                case '8 Post (19-26)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SS'
                                    else:
                                        prim_assigned = 'FS'
                                case '9 Fade (27-39)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'RCB'
                                    else:
                                        prim_assigned = 'SS'
                                case 'W Wheel (9-18)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'RCB'
                                    else:
                                        prim_assigned = 'SS'
                                case 'D Deep Fade (40+)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'RCB'
                                    else:
                                        prim_assigned = 'SS'    
                        elif ('Cover-3 Sky' in def_formation):
                            match route:
                                case 'S Screen (S)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    elif('Nickel Personnel' in def_formation):
                                        if ('43' in def_formation):
                                            prim_assigned = 'SS'
                                        else:
                                            prim_assigned = 'SLB'
                                    elif('Dime Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                case 'F Flat (0-4)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    elif('Nickel Personnel' in def_formation):
                                        if ('43' in def_formation):
                                            prim_assigned = 'SS'
                                        else:
                                            prim_assigned = 'SLB'
                                    elif('Dime Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                case '0 Dig (0-4)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Dime Personnel' in def_formation):
                                            prim_assigned = 'SS'
                                        else:
                                            prim_assigned = 'SILB'
                                case '1 Out (5-8)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    elif('Nickel Personnel' in def_formation):
                                        if ('43' in def_formation):
                                            prim_assigned = 'SS'
                                        else:
                                            prim_assigned = 'SLB'
                                    elif('Dime Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                case '2 Slant (5-8)':
                                    if('Regular' in def_formation):
                                        prim_assigned = 'SS'
                                    elif('Nickel Personnel' in def_formation):
                                        if ('43' in def_formation):
                                            prim_assigned = 'MLB'
                                        else:
                                            prim_assigned = 'SS'
                                    elif('Dime Personnel' in def_formation):
                                        if ('43' in def_formation):
                                            prim_assigned = 'SS'
                                        else:
                                            prim_assigned = 'SLB'
                                case '3 Comeback (9-12)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    elif('Nickel Personnel' in def_formation):
                                        if ('43' in def_formation):
                                            prim_assigned = 'SS'
                                        else:
                                            prim_assigned = 'SLB'
                                    elif('Dime Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                case '4 Curl (9-12)':
                                    if('Regular' in def_formation):
                                        prim_assigned = 'SS'
                                    elif('Nickel Personnel' in def_formation):
                                        if ('43' in def_formation):
                                            prim_assigned = 'MLB'
                                        else:
                                            prim_assigned = 'SS'
                                    elif('Dime Personnel' in def_formation):
                                        if ('43' in def_formation):
                                            prim_assigned = 'SS'
                                        else:
                                            prim_assigned = 'SLB'
                                case '5 Deep Out (13-18)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif('Nickel Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif('Dime Personnel' in def_formation):
                                        prim_assigned = 'DB'
                                case '6 Deep In (13-18)':
                                    prim_assigned = 'FS'
                                case '7 Corner (19-26)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif('Nickel Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif('Dime Personnel' in def_formation):
                                        prim_assigned = 'DB'
                                case '8 Post (19-26)':
                                    prim_assigned = 'FS'
                                case '9 Fade (27-39)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif('Nickel Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif('Dime Personnel' in def_formation):
                                        prim_assigned = 'DB'
                                case 'W Wheel (9-18)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif('Nickel Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif('Dime Personnel' in def_formation):
                                        prim_assigned = 'DB'
                                case 'D Deep Fade (40+)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif('Nickel Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif('Dime Personnel' in def_formation):
                                        prim_assigned = 'DB'                                                                     
                        elif ('Cover-4' in def_formation):
                            match route:
                                case 'S Screen (S)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    else:
                                        if('43' in def_formation):
                                            prim_assigned = 'MLB'
                                        elif ('34' in def_formation):
                                            prim_assigned = 'SLB'
                                case 'F Flat (0-4)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    else:
                                        if('43' in def_formation):
                                            prim_assigned = 'MLB'
                                        elif ('34' in def_formation):
                                            prim_assigned = 'SLB'
                                case '0 Dig (0-4)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                            prim_assigned = 'SILB'
                                        elif('Dime Personnel' in def_formation):
                                            prim_assigned = 'SLB'
                                case '1 Out (5-8)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    else:
                                        if('43' in def_formation):
                                            prim_assigned = 'MLB'
                                        elif ('34' in def_formation):
                                            prim_assigned = 'SLB'
                                case '2 Slant (5-8)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                            prim_assigned = 'SILB'
                                        elif('Dime Personnel' in def_formation):
                                            prim_assigned = 'SLB'
                                case '3 Comeback (9-12)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    else:
                                        if('43' in def_formation):
                                            prim_assigned = 'MLB'
                                        elif ('34' in def_formation):
                                            prim_assigned = 'SLB'
                                case '4 Curl (9-12)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                            prim_assigned = 'SILB'
                                        elif('Dime Personnel' in def_formation):
                                            prim_assigned = 'SLB'
                                case '5 Deep Out (13-18)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif('Nickel Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif('Dime Personnel' in def_formation):
                                        prim_assigned = 'DB'
                                case '6 Deep In (13-18)':
                                    prim_assigned = 'SS'
                                case '7 Corner (19-26)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif('Nickel Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif('Dime Personnel' in def_formation):
                                        prim_assigned = 'DB'
                                case '8 Post (19-26)':
                                    prim_assigned = 'SS'
                                case '9 Fade (27-39)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif('Nickel Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif('Dime Personnel' in def_formation):
                                        prim_assigned = 'DB'
                                case 'W Wheel (9-18)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                            prim_assigned = 'SILB'
                                        elif('Dime Personnel' in def_formation):
                                            prim_assigned = 'SLB'
                                case 'D Deep Fade (40+)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif('Nickel Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif('Dime Personnel' in def_formation):
                                        prim_assigned = 'DB'
                                        
                    elif (position == 'R' and '014' in off_formation or
                          position == 'R' and '023' in off_formation or
                          position == 'R' and '113' in off_formation or
                          position == 'V'
                          ):
                          if ('Man to Man' in def_formation or
                              'Cover-2' in def_formation or
                              'Cover-1' in def_formation or                              
                              'Press-2' in def_formation or
                              'Press-1' in def_formation or
                              'Tampa-2' in def_formation
                              ):
                             prim_assigned = 'NB'
                             if position == 'V':
                                 if ('Man to Man' in def_formation or
                                     'Cover-1' in def_formation or
                                     'Press-1' in def_formation
                                     ):
                                     prim_assigned = 'SS'
                                 else:
                                     prim_assigned = 'None'
                          elif ('Cover-3 Cloud' in def_formation):
                                 match route:
                                    case 'S Screen (S)':
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'WLB'
                                        elif ('Nickel Personnel' in def_formation):
                                            prim_assigned = 'WLB'
                                        elif ('Dime Personnel' in def_formation):
                                            prim_assigned = 'NB'
                                    case 'F Flat (0-4)':
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'WLB'
                                        elif ('Nickel Personnel' in def_formation):
                                            prim_assigned = 'WLB'
                                        elif ('Dime Personnel' in def_formation):
                                            prim_assigned = 'NB'
                                    case '0 Dig (0-4)':
                                        if ('43' in def_formation):
                                            prim_assigned = 'MLB'                                    
                                        elif ('34' in def_formation):
                                            if ('Dime' in def_formation):
                                                prim_assigned = 'WLB'                            
                                            elif ('Nickel' in def_formation):
                                                prim_assigned = 'SILB'
                                            elif ('Regular' in def_formation):
                                                prim_assigned = 'WILB'
                                    case '1 Out (5-8)':
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'WLB'
                                        elif ('Nickel Personnel' in def_formation):
                                            prim_assigned = 'WLB'
                                        elif ('Dime Personnel' in def_formation):
                                            prim_assigned = 'NB'
                                    case '2 Slant (5-8)':
                                        if ('43' in def_formation):
                                            prim_assigned = 'MLB'
                                        elif ('34' in def_formation):
                                            if ('Dime Personnel' in def_formation):
                                                prim_assigned = 'WLB'                            
                                            elif ('Nickel Personnels' in def_formation):
                                                prim_assigned = 'SILB'
                                            elif ('Regular' in def_formation):
                                                prim_assigned = 'WILB'
                                    case '3 Comeback (9-12)':
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'WLB'
                                        elif ('Nickel Personnel' in def_formation):
                                            prim_assigned = 'WLB'
                                        elif ('Dime Personnel' in def_formation):
                                            if('43' in def_formation):
                                                prim_assigned = 'DB'
                                            elif ('34'in def_formation):
                                                prim_assigned = 'WLB'
                                    case '4 Curl (9-12)':
                                        if ('43' in def_formation):
                                            prim_assigned = 'MLB'                                    
                                        elif ('34' in def_formation):
                                            if ('Dime' in def_formation):
                                                prim_assigned = 'WLB'                            
                                            elif ('Nickel' in def_formation):
                                                prim_assigned = 'SILB'
                                            elif ('Regular' in def_formation):
                                                prim_assigned = 'WILB'
                                    case '5 Deep Out (13-18)':
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'FS'
                                        elif ('Nickel Personnel' in def_formation):
                                            prim_assigned = 'NB'
                                        elif ('Dime Personnel' in def_formation):
                                            prim_assigned = 'DB'
                                    case '6 Deep In (13-18)':
                                        prim_assigned = 'FS'
                                    case '7 Corner (19-26)':
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'FS'
                                        elif ('Nickel Personnel' in def_formation):
                                            prim_assigned = 'NB'
                                        elif ('Dime Personnel' in def_formation):
                                            prim_assigned = 'DB'
                                    case '8 Post (19-26)':
                                        prim_assigned = 'FS'
                                    case '9 Fade (27-39)':
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'FS'
                                        elif ('Nickel Personnel' in def_formation):
                                            prim_assigned = 'NB'
                                        elif ('Dime Personnel' in def_formation):
                                            prim_assigned = 'DB'
                                    case 'W Wheel (9-18)':
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'FS'
                                        elif ('Nickel Personnel' in def_formation):
                                            prim_assigned = 'NB'
                                        elif ('Dime Personnel' in def_formation):
                                            prim_assigned = 'DB'
                                    case 'D Deep Fade (40+)':
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'FS'
                                        elif ('Nickel Personnel' in def_formation):
                                            prim_assigned = 'NB'
                                        elif ('Dime Personnel' in def_formation):
                                            prim_assigned = 'DB'
                          elif ('Cover-3 Sky' in def_formation):
                                 match route:
                                    case 'S Screen (S)':
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'WLB'
                                        else:
                                            prim_assigned = 'LCB'
                                    case 'F Flat (0-4)':
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'WLB'
                                        else:
                                            prim_assigned = 'LCB'
                                    case '0 Dig (0-4)':
                                        if ('43' in def_formation):
                                          if ('Dime Personnel' in def_formation):
                                              prim_assigned = 'MLB'                                        
                                          elif('Nickel Personnel' in def_formation):
                                              prim_assigned = 'WLB'                                        
                                          else:
                                              prim_assigned = 'MLB'                                    
                                        elif ('34' in def_formation):
                                          if ('Dime Personnel' in def_formation):
                                              prim_assigned = 'WLB'                                        
                                          elif('Nickel Personnel' in def_formation):
                                              prim_assigned = 'WLB'                                        
                                          else:
                                              prim_assigned = 'WILB'
                                    case '1 Out (5-8)':
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'WLB'
                                        else:
                                            prim_assigned = 'LCB'
                                    case '2 Slant (5-8)':
                                        if ('43' in def_formation):
                                            if ('Dime Personnel' in def_formation):
                                                prim_assigned = 'MLB'                                        
                                            elif('Nickel Personnel' in def_formation):
                                                prim_assigned = 'WLB'                                        
                                            else:
                                                prim_assigned = 'MLB'
                                        elif ('34' in def_formation):
                                            if ('Dime Personnel' in def_formation):
                                                prim_assigned = 'WLB'                                        
                                            elif('Nickel Personnel' in def_formation):
                                                prim_assigned = 'WLB'                                        
                                            else:
                                                prim_assigned = 'WILB'
                                    case '3 Comeback (9-12)':
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'WLB'                                    
                                        else:
                                            prim_assigned = 'LCB'
                                    case '4 Curl (9-12)':
                                        if ('43' in def_formation):
                                            if ('Dime Personnel' in def_formation):
                                                prim_assigned = 'MLB'                                        
                                            elif('Nickel Personnel' in def_formation):
                                                prim_assigned = 'WLB'                                        
                                            else:
                                                prim_assigned = 'MLB'
                                        elif ('34' in def_formation):
                                            if ('Dime Personnel' in def_formation):
                                                prim_assigned = 'WLB'                                        
                                            elif('Nickel Personnel' in def_formation):
                                                prim_assigned = 'WLB'                                        
                                            else:
                                                prim_assigned = 'WILB'
                                    case '5 Deep Out (13-18)':
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'LCB'
                                        else:
                                            prim_assigned = 'NB'
                                    case '6 Deep In (13-18)':
                                        prim_assigned = 'FS'
                                    case '7 Corner (19-26)':
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'LCB'
                                        else:
                                            prim_assigned = 'NB'
                                    case '8 Post (19-26)':
                                        prim_assigned = 'FS'
                                    case '9 Fade (27-39)':
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'LCB'
                                        else:
                                            prim_assigned = 'NB'
                                    case 'W Wheel (9-18)':
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'LCB'
                                        else:
                                            prim_assigned = 'NB'
                                    case 'D Deep Fade (40+)':
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'LCB'
                                        else:
                                            prim_assigned = 'NB'                                                                      
                          elif ('Cover-4' in def_formation):
                              match route:
                                case 'S Screen (S)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'WLB'
                                    else:
                                        prim_assigned = 'LCB'
                                case 'F Flat (0-4)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'WLB'
                                    else:
                                        prim_assigned = 'LCB'
                                case '0 Dig (0-4)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                            prim_assigned = 'SILB'
                                        elif('Dime Personnel' in def_formation):
                                            prim_assigned = 'SLB'
                                case '1 Out (5-8)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'WLB'
                                    else:
                                        prim_assigned = 'LCB'
                                case '2 Slant (5-8)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                            prim_assigned = 'SILB'
                                        elif('Dime Personnel' in def_formation):
                                            prim_assigned = 'SLB'
                                case '3 Comeback (9-12)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'WLB'
                                    else:
                                        prim_assigned = 'LCB'
                                case '4 Curl (9-12)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                            prim_assigned = 'SILB'
                                        elif('Dime Personnel' in def_formation):
                                            prim_assigned = 'SLB'
                                case '5 Deep Out (13-18)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'LCB'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        prim_assigned = 'NB'
                                case '6 Deep In (13-18)':
                                    prim_assigned = 'FS'
                                case '7 Corner (19-26)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'LCB'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        prim_assigned = 'NB'
                                case '8 Post (19-26)':
                                    prim_assigned = 'FS'
                                case '9 Fade (27-39)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'LCB'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        prim_assigned = 'NB'
                                case 'W Wheel (9-18)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'WLB'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        prim_assigned = 'LCB'
                                case 'D Deep Fade (40+)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'LCB'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        prim_assigned = 'NB'                           
                    
                    elif (position == 'R' and '005' in off_formation or
                          position == 'R' and '014t' in off_formation or
                          position == 'R' and '113t' in off_formation or
                          position == 'R' and '203' in off_formation or
                          position == 'S'
                          ):
                        if ('Man to Man' in def_formation or
                            'Cover-2' in def_formation or
                            'Cover-1' in def_formation or                            
                            'Press-2' in def_formation or
                            'Press-1' in def_formation or
                            'Tampa-2' in def_formation
                            ):
                            if (position == 'R'):
                                prim_assigned = 'NB' 
                            elif (position == 'S'):
                                prim_assigned = 'DB'
                        elif ('Cover-3 Cloud' in def_formation):
                             match route:
                                case 'S Screen (S)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'WLB'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        prim_assigned = 'NB'
                                case 'F Flat (0-4)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        prim_assigned = 'RCB'    
                                case '0 Dig (0-4)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'                                    
                                    elif ('34' in def_formation):
                                        if ('Dime Personnel' in def_formation):
                                            prim_assigned = 'NB'                                        
                                        else:
                                            prim_assigned = 'SILB'
                                case '1 Out (5-8)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                case '2 Slant (5-8)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                            prim_assigned = 'SLB'
                                        else:
                                            prim_assigned = 'SILB'
                                case '3 Comeback (9-12)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        prim_assigned = 'RCB'                                       
                                case '4 Curl (9-12)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                            prim_assigned = 'SLB'
                                        else:
                                            prim_assigned = 'SILB'
                                case '5 Deep Out (13-18)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'RCB'
                                    else:
                                        prim_assigned = 'SS'
                                case '6 Deep In (13-18)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SS'
                                    else:
                                        prim_assigned = 'FS'
                                case '7 Corner (19-26)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'RCB'
                                    else:
                                        prim_assigned = 'SS'
                                case '8 Post (19-26)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SS'
                                    else:
                                        prim_assigned = 'FS'
                                case '9 Fade (27-39)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'RCB'
                                    else:
                                        prim_assigned = 'SS'
                                case 'W Wheel (9-18)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'RCB'
                                    else:
                                        prim_assigned = 'SS'                                   
                                case 'D Deep Fade (40+)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'RCB'
                                    else:
                                        prim_assigned = 'SS'                                 
                        elif ('Cover-3 Sky' in def_formation):
                            match route:
                                case 'S Screen (S)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'WLB'
                                    elif ('Nickel Personnel' in def_formation):
                                        if('43' in def_formation):
                                            prim_assigned = 'SS'
                                        else:
                                            prim_assigned = 'SLB'
                                    elif ('Dime Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                case 'F Flat (0-4)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    elif ('Nickel Personnel' in def_formation):
                                        if('43' in def_formation):
                                            prim_assigned = 'SS'
                                        else:
                                            prim_assigned = 'SLB'
                                    elif ('Dime Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                case '0 Dig (0-4)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'                                    
                                    elif ('34' in def_formation):
                                        if ('Dime Personnel' in def_formation):
                                            prim_assigned = 'SS'                                        
                                        else:
                                            prim_assigned = 'SILB'
                                case '1 Out (5-8)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    elif ('Nickel Personnel' in def_formation):
                                        if('43' in def_formation):
                                            prim_assigned = 'SS'
                                        else:
                                            prim_assigned = 'SLB'
                                    elif ('Dime Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                case '2 Slant (5-8)':
                                    if('Regular' in def_formation):
                                        prim_assigned = 'SS'
                                    elif ('Nickel Personnel' in def_formation):
                                        if('43' in def_formation):
                                            prim_assigned = 'MLB'
                                        else:
                                            prim_assigned = 'SS'
                                    elif ('Dime Personnel' in def_formation):
                                        if('43' in def_formation):
                                            prim_assigned = 'SS'
                                        else:
                                            prim_assigned = 'SLB'
                                case '3 Comeback (9-12)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    elif ('Nickel Personnel' in def_formation):
                                        if('43' in def_formation):
                                            prim_assigned = 'SS'
                                        else:
                                            prim_assigned = 'SLB'
                                    elif ('Dime Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                case '4 Curl (9-12)':
                                    if('Regular' in def_formation):
                                        prim_assigned = 'SS'
                                    elif ('Nickel Personnel' in def_formation):
                                        if('43' in def_formation):
                                            prim_assigned = 'MLB'
                                        else:
                                            prim_assigned = 'SS'
                                    elif ('Dime Personnel' in def_formation):
                                        if('43' in def_formation):
                                            prim_assigned = 'SS'
                                        else:
                                            prim_assigned = 'SLB'
                                case '5 Deep Out (13-18)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif ('Nickel Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif ('Dime Personnel' in def_formation):
                                        prim_assigned = 'DB'
                                case '6 Deep In (13-18)':
                                    prim_assigned = 'FS'
                                case '7 Corner (19-26)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif ('Nickel Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif ('Dime Personnel' in def_formation):
                                        prim_assigned = 'DB'
                                case '8 Post (19-26)':
                                    prim_assigned = 'FS'                                 
                                case '9 Fade (27-39)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif ('Nickel Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif ('Dime Personnel' in def_formation):
                                        prim_assigned = 'DB'
                                case 'W Wheel (9-18)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif ('Nickel Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif ('Dime Personnel' in def_formation):
                                        prim_assigned = 'DB'                                  
                                case 'D Deep Fade (40+)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif ('Nickel Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif ('Dime Personnel' in def_formation):
                                        prim_assigned = 'DB'                                                                                               
                        elif ('Cover-4' in def_formation):
                             match route:
                                case 'S Screen (S)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    else:
                                        if ('43' in def_formation):
                                            prim_assigned = 'MLB'
                                        elif ('34' in def_formation):
                                            prim_assigned = 'SLB'
                                case 'F Flat (0-4)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    else:
                                        if ('43' in def_formation):
                                            prim_assigned = 'MLB'
                                        elif ('34' in def_formation):
                                            prim_assigned = 'SLB'
                                case '0 Dig (0-4)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                            prim_assigned = 'SILB'
                                        elif('Dime Personnel' in def_formation):
                                            prim_assigned = 'SLB'
                                case '1 Out (5-8)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    else:
                                        if ('43' in def_formation):
                                            prim_assigned = 'MLB'
                                        elif ('34' in def_formation):
                                            prim_assigned = 'SLB'
                                case '2 Slant (5-8)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                            prim_assigned = 'SILB'
                                        elif('Dime Personnel' in def_formation):
                                            prim_assigned = 'SLB'
                                case '3 Comeback (9-12)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    else:
                                        if ('43' in def_formation):
                                            prim_assigned = 'MLB'
                                        elif ('34' in def_formation):
                                            prim_assigned = 'SLB'
                                case '4 Curl (9-12)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                            prim_assigned = 'SILB'
                                        elif('Dime Personnel' in def_formation):
                                            prim_assigned = 'SLB'
                                case '5 Deep Out (13-18)':
                                    if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif ('Dime Personnel' in def_formation):
                                        prim_assigned = 'DB'
                                case '6 Deep In (13-18)':
                                    prim_assigned = 'SS'
                                case '7 Corner (19-26)':
                                    if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif ('Dime Personnel' in def_formation):
                                        prim_assigned = 'DB'
                                case '8 Post (19-26)':
                                    prim_assigned = 'SS'
                                case '9 Fade (27-39)':
                                    if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif ('Dime Personnel' in def_formation):
                                        prim_assigned = 'DB'
                                case 'W Wheel (9-18)':
                                    if('43' in def_formation):
                                         prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                            prim_assigned = 'SILB'
                                        elif('Dime Personnel' in def_formation):
                                            prim_assigned = 'SLB'
                                case 'D Deep Fade (40+)':
                                    if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif ('Dime Personnel' in def_formation):
                                        prim_assigned = 'DB'                                
                    
                    elif ((position == 'Y' and '014t' in off_formation) or 
                          (position == 'T' and '023' in off_formation) or
                          (position == 'T' and '122' in off_formation)
                          (position == 'T' and '131' in off_formation)
                          ):
                        if ('Man to Man' in def_formation or
                            'Cover-2' in def_formation or
                            'Cover-1' in def_formation or                              
                            'Press-2' in def_formation or
                            'Press-1' in def_formation or
                            'Tampa-2' in def_formation
                            ):                            
                            if (('Cover-2' in def_formation) or
                                ('Press-2' in def_formation) or
                                ('Tampa-2' in def_formation)
                                ):
                                if ('Regular' in def_formation or 'Nickel' in def_formation):
                                    prim_assigned = 'WLB'
                                else:
                                    if ('43' in def_formation):
                                        if 'Tampa-2' in def_formation:
                                            prim_assigned = 'WLB'
                                        else:
                                            prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        prim_assigned = 'WLB'
                            else:
                                if position == 'Y':
                                    prim_assigned = 'SS'
                                elif position == 'T':
                                    if ('Regular' in def_formation):    
                                        prim_assigned = 'WLB'
                                    elif ('Nickel' in def_formation or 'Dime' in def_formation):
                                        if '023' in off_formation:
                                            prim_assigned = 'WLB'
                                        else:
                                            prim_assigned = 'NB'
                        elif ('Cover-3 Cloud' in def_formation):
                            match route:
                                case 'S Screen (S)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'WLB'
                                    elif ('Nickel Personnel' in def_formation):
                                        if('43' in def_formation):
                                            prim_assigned = 'WLB'
                                    elif ('Dime Personnel' in def_formation):
                                        prim_assigned = 'NB'
                                case 'F Flat (0-4)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'WLB'
                                    elif ('Nickel Personnel' in def_formation):
                                        prim_assigned = 'WLB'
                                    elif ('Dime Personnel' in def_formation):
                                        prim_assigned = 'NB'
                                case '0 Dig (0-4)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Dime Personnel' in def_formation):
                                            prim_assigned = 'WLB'                                        
                                        elif('Nickel Personnel' in def_formation):
                                            prim_assigned = 'SILB'
                                        else:
                                            prim_assigned = 'WILB'
                                case '1 Out (5-8)':
                                    if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                        prim_assigned = 'WLB'
                                    elif ('Dime Personnel' in def_formation):
                                        prim_assigned = 'NB'
                                case '2 Slant (5-8)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Dime Personnel' in def_formation):
                                            prim_assigned = 'WLB'                                        
                                        elif('Nickel Personnel' in def_formation):
                                            prim_assigned = 'SILB'
                                        else:
                                            prim_assigned = 'WILB'
                                case '3 Comeback (9-12)':
                                    if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                        prim_assigned = 'WLB'
                                    elif ('Dime Personnel' in def_formation):
                                        if('43' in def_formation):
                                            prim_assigned = 'DB'
                                        elif ('34' in def_formation):
                                            prim_assigned = 'WLB'
                                case '4 Curl (9-12)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Dime Personnel' in def_formation):
                                            prim_assigned = 'WLB'                                        
                                        elif('Nickel Personnel' in def_formation):
                                            prim_assigned = 'SILB'
                                        else:
                                            prim_assigned = 'WILB'                              
                                case '5 Deep Out (13-18)':
                                    if('Regular' in def_formation):
                                        prim_assigned = 'FS'
                                    elif ('Nickel Personnel' in def_formation):
                                        prim_assigned = 'NB'
                                    elif ('Dime Personnel' in def_formation):
                                        prim_assigned = 'DB'
                                case '6 Deep In (13-18)':
                                    prim_assigned = 'FS'                          
                                case '7 Corner (19-26)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'FS'
                                    elif ('Nickel Personnel' in def_formation):
                                        prim_assigned = 'NB'
                                    elif ('Dime Personnel' in def_formation):
                                        prim_assigned = 'DB'                               
                                case '8 Post (19-26)':
                                    prim_assigned = 'FS'
                                case '9 Fade (27-39)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'FS'
                                    elif ('Nickel Personnel' in def_formation):
                                        prim_assigned = 'NB'
                                    elif ('Dime Personnel' in def_formation):
                                        prim_assigned = 'DB'
                                case 'W Wheel (9-18)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'FS'
                                    elif ('Nickel Personnel' in def_formation):
                                        prim_assigned = 'NB'
                                    elif ('Dime Personnel' in def_formation):
                                        prim_assigned = 'DB'                                   
                                case 'D Deep Fade (40+)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'FS'
                                    elif ('Nickel Personnel' in def_formation):
                                        prim_assigned = 'NB'
                                    elif ('Dime Personnel' in def_formation):
                                        prim_assigned = 'DB'                               
                        elif ('Cover-3 Sky' in def_formation):
                            match route:
                                case 'S Screen (S)':
                                    if ('Regular' in def_formation):
                                        if('43' in def_formation):
                                            prim_assigned = 'WLB'
                                        elif ('34' in def_formation):
                                            prim_assigned = 'WILB'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        if('43' in def_formation):
                                            prim_assigned = 'LCB'
                                        elif ('34' in def_formation):
                                            prim_assigned = 'WLB'
                                case 'F Flat (0-4)':
                                    if ('Regular' in def_formation):
                                        if('43' in def_formation):
                                            prim_assigned = 'WLB'
                                        elif ('34' in def_formation):
                                            prim_assigned = 'WILB'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        if('43' in def_formation):
                                            prim_assigned = 'LCB'
                                        elif ('34' in def_formation):
                                            prim_assigned = 'WLB'                                   
                                case '0 Dig (0-4)':
                                    if ('43' in def_formation):
                                        if ('Dime Personnel' in def_formation):
                                            prim_assigned = 'MLB'                                        
                                        elif('Nickel Personnel' in def_formation):
                                            prim_assigned = 'WLB'                                        
                                        else:
                                            prim_assigned = 'MLB'         
                                    elif ('34' in def_formation):
                                        if ('Dime Personnel' in def_formation):
                                            prim_assigned = 'SS'
                                        else:
                                            prim_assigned = 'SILB'                   
                                case '1 Out (5-8)':
                                    if ('Regular' in def_formation):
                                        if('43' in def_formation):
                                            prim_assigned = 'WLB'
                                        elif ('34' in def_formation):
                                            prim_assigned = 'WILB'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        if('43' in def_formation):
                                            prim_assigned = 'LCB'
                                        elif ('34' in def_formation):
                                            prim_assigned = 'WLB'                                            
                                case '2 Slant (5-8)':
                                    if ('43' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'MLB'                                        
                                        elif('Nickel' in def_formation):
                                            prim_assigned = 'WLB'                                        
                                        else:
                                            prim_assigned = 'MLB'                                    
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'SS'
                                        else:
                                            prim_assigned = 'SILB'                                    
                                case '3 Comeback (9-12)':
                                    if ('Regular' in def_formation):
                                        if('43' in def_formation):
                                            prim_assigned = 'WLB'
                                        elif ('34' in def_formation):
                                            prim_assigned = 'WILB'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        if('43' in def_formation):
                                            prim_assigned = 'LCB'
                                        elif ('34' in def_formation):
                                            prim_assigned = 'WLB'                                                  
                                case '4 Curl (9-12)':
                                    if ('43' in def_formation):
                                        if ('Dime Personnel' in def_formation):
                                            prim_assigned = 'MLB'                                        
                                        elif('Nickel Personnel' in def_formation):
                                            prim_assigned = 'WLB'                                        
                                        else:
                                            prim_assigned = 'MLB'     
                                    elif ('34' in def_formation):
                                        if ('Dime Personnel' in def_formation):
                                            prim_assigned = 'SS'
                                        else:
                                            prim_assigned = 'SILB'                                          
                                case '5 Deep Out (13-18)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'LCB'
                                    else:
                                        prim_assigned = 'NB'
                                case '6 Deep In (13-18)':
                                    prim_assigned = 'FS'
                                case '7 Corner (19-26)':
                                    if('Regular' in def_formation):
                                        prim_assigned = 'LCB'
                                    else:
                                        prim_assigned = 'NB'
                                case '8 Post (19-26)':
                                    prim_assigned = 'FS'                                  
                                case '9 Fade (27-39)':
                                    prim_assigned = 'FS'                             
                                case 'W Wheel (9-18)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'LCB'
                                    else:
                                        prim_assigned = 'NB'                                 
                                case 'D Deep Fade (40+)':
                                    prim_assigned = 'FS'                                                                                                     
                        elif ('Cover-4' in def_formation):
                            match route:
                                case 'S Screen (S)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'WLB'
                                    else:
                                        prim_assigned = 'LCB'
                                case 'F Flat (0-4)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'WLB'
                                    else:
                                        prim_assigned = 'LCB'
                                case '0 Dig (0-4)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                            prim_assigned = 'SILB'
                                        elif('Dime Personnel' in def_formation):
                                            prim_assigned = 'SLB'
                                case '1 Out (5-8)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'WLB'
                                    else:
                                        prim_assigned = 'LCB'
                                case '2 Slant (5-8)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                            prim_assigned = 'SILB'
                                        elif('Dime Personnel' in def_formation):
                                            prim_assigned = 'SLB'
                                case '3 Comeback (9-12)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'WLB'
                                    else:
                                        prim_assigned = 'LCB'
                                case '4 Curl (9-12)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                            prim_assigned = 'SILB'
                                        elif('Dime Personnel' in def_formation):
                                            prim_assigned = 'SLB'
                                case '5 Deep Out (13-18)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'LCB'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        prim_assigned = 'NB'
                                case '6 Deep In (13-18)':
                                    prim_assigned = 'FS'
                                case '7 Corner (19-26)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'LCB'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        prim_assigned = 'NB'
                                case '8 Post (19-26)':
                                    prim_assigned = 'FS'
                                case '9 Fade (27-39)':
                                    prim_assigned = 'FS'
                                case 'W Wheel (9-18)':
                                    prim_assigned = 'FS'
                                case 'D Deep Fade (40+)':
                                    prim_assigned = 'FS'
                    
                    elif ((position == 'Y' and '014' in off_formation) or
                          (position == 'Y' and '113' in off_formation) or
                          (position == 'Y' and '122' in off_formation) or
                          (position == 'Y' and '221' in off_formation) or
                          (position == 'Y' and '113t' in off_formation) or
                          (position == 'Y' and '131' in off_formation) or
                          (position == 'Y' and '212' in off_formation) or
                          (position == 'Y' and '230' in off_formation) or
                          (position == 'Y' and '023' in off_formation)
                          ):
                        if ('Man to Man' in def_formation or
                            'Cover-2' in def_formation or
                            'Cover-1' in def_formation or                              
                            'Press-2' in def_formation or
                            'Press-1' in def_formation or
                            'Tampa-2' in def_formation
                            ):                            
                            if (('Cover-2' in def_formation) or
                                ('Press-2' in def_formation) or
                                ('Tampa-2' in def_formation)
                                ):
                                if ('Regular' in def_formation or 'Nickel' in def_formation):
                                    if ('43' in def_formation):
                                        if 'Tampa-2' in def_formation:
                                            prim_assigned = 'SLB'
                                        else:
                                            prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        prim_assigned = 'SILB'
                                else:
                                    if ('43' in def_formation):
                                        if 'Tampa-2' in def_formation:
                                            prim_assigned = 'SLB'
                                        else:
                                            prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        prim_assigned = 'SLB'
                            else:
                                prim_assigned = 'SS'
                        elif ('Cover-3 Cloud' in def_formation):
                            match route:
                                case 'S Screen (S)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                case 'F Flat (0-4)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                case '0 Dig (0-4)':
                                    if('43' in def_formation):
                                        prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Dime Personnel' in def_formation or 'Regular' in def_formation):
                                            prim_assigned = 'SILB'                                        
                                        elif('Nickel Personnel' in def_formation):
                                            prim_assigned = 'SLB'
                                case '1 Out (5-8)':
                                    if('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                case '2 Slant (5-8)':
                                    if('43' in def_formation):
                                        prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'SILB'                                        
                                        elif('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                            prim_assigned = 'SLB'                                        
                                case '3 Comeback (9-12)':
                                    if('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    elif('Nickel Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif('Dime Personnel' in def_formation):
                                        if('43' in def_formation):
                                            prim_assigned = 'RCB'
                                        elif ('34'in def_formation):
                                            prim_assigned = 'SLB'                                       
                                case '4 Curl (9-12)':
                                    if('43' in def_formation):
                                        prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Dime Personnel' in def_formation or 'Nickel Personnel' in def_formation):
                                            prim_assigned = 'SLB'                                        
                                        elif('Regular' in def_formation):
                                            prim_assigned = 'SILB'                                 
                                case '5 Deep Out (13-18)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        prim_assigned = 'SS'                                      
                                case '6 Deep In (13-18)':
                                    if('Regular' in def_formation):
                                        prim_assigned = 'SS'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        prim_assigned = 'FS'
                                case '7 Corner (19-26)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        prim_assigned = 'SS'                             
                                case '8 Post (19-26)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SS'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        prim_assigned = 'FS'                                        
                                case '9 Fade (27-39)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SS'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        prim_assigned = 'FS'
                                case 'W Wheel (9-18)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        prim_assigned = 'SS'                                  
                                case 'D Deep Fade (40+)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SS'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        prim_assigned = 'FS'                              
                        elif ('Cover-3 Sky' in def_formation):
                            match route:
                                case 'S Screen (S)':
                                    if ('Regular' in def_formation):
                                        if '43' in def_formation:
                                            prim_assigned = 'SS'
                                        elif '34' in def_formation:
                                            prim_assigned = 'SILB'
                                    elif ('Nickel' in def_formation or 'Dime' in def_formation):
                                        if '43' in def_formation:
                                            prim_assigned = 'SS'
                                        elif '34' in def_formation:
                                            prim_assigned = 'SS'                                          
                                case 'F Flat (0-4)':
                                    if ('Regular' in def_formation):
                                        if '43' in def_formation:
                                            prim_assigned = 'SS'
                                        elif '34' in def_formation:
                                            prim_assigned = 'SILB'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        prim_assigned = 'SS'    
                                case '0 Dig (0-4)':
                                    if ('43' in def_formation):
                                        if ('Nickel Personnel' in def_formation):
                                            prim_assigned = 'MLB'                                                                               
                                        else:
                                            prim_assigned = 'SS'                                    
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'SS'
                                        else:
                                            prim_assigned = 'SILB'   
                                case '1 Out (5-8)':
                                    if ('Regular' in def_formation):
                                        if '43' in def_formation:
                                            prim_assigned = 'SS'
                                        elif '34' in def_formation:
                                            prim_assigned = 'SILB'
                                    elif ('Nickel Personnel' in def_formation or 'Dime Personnel' in def_formation):
                                        prim_assigned = 'SS'  
                                case '2 Slant (5-8)':                                                                                                                               
                                    if ('43' in def_formation):
                                        if ('Nickel Personnel' in def_formation):
                                            prim_assigned = 'MLB'                                                                               
                                        else:
                                            prim_assigned = 'SS'
                                    elif ('34' in def_formation):
                                        if ('Dime Personnel' in def_formation):
                                            prim_assigned = 'SS'
                                        else:
                                            prim_assigned = 'SILB'                     
                                case '3 Comeback (9-12)':
                                    if ('Regular' in def_formation):
                                        if '43' in def_formation:
                                            prim_assigned = 'SLB'
                                        elif '34' in def_formation:
                                            prim_assigned = 'SS'
                                    elif ('Nickel Personnel' in def_formation):
                                        prim_assigned = 'SS'
                                    elif ('Dime Personnel' in def_formation):
                                        if '43' in def_formation:
                                            prim_assigned = 'RCB'
                                        elif '34' in def_formation:
                                            prim_assigned = 'SLB'                                      
                                case '4 Curl (9-12)':
                                    if ('43' in def_formation):
                                        if ('Nickel Personnel' in def_formation):
                                            prim_assigned = 'MLB'                                                                               
                                        else:
                                            prim_assigned = 'SS'
                                    elif ('34' in def_formation):
                                        if ('Dime Personnel' in def_formation):
                                            prim_assigned = 'SS'
                                        else:
                                            prim_assigned = 'SILB'
                                case '5 Deep Out (13-18)':
                                    if ('Dime Personnel' in def_formation):
                                        prim_assigned = 'DB'
                                    elif ('Nickel Personnel' in def_formation or 'Regular' in def_formation):
                                        prim_assigned = 'RCB'                                      
                                case '6 Deep In (13-18)':
                                    prim_assigned = 'FS'
                                case '7 Corner (19-26)':
                                    if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                        prim_assigned = 'RCB'   
                                    elif ('Dime Personnel' in def_formation):
                                        prim_assigned = 'DB'                          
                                case '8 Post (19-26)':
                                    prim_assigned = 'FS'                                  
                                case '9 Fade (27-39)':
                                    prim_assigned = 'FS'
                                case 'W Wheel (9-18)':                             
                                    if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif ('Dime Personnel' in def_formation):
                                        prim_assigned = 'DB'                                  
                                case 'D Deep Fade (40+)':
                                    prim_assigned = 'FS'                                                                                                     
                        elif ('Cover-4' in def_formation):
                            match route:
                                case 'S Screen (S)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    elif('Nickel Personnel' in def_formation):
                                        if('43' in def_formation):
                                            prim_assigned = 'MLB'
                                        elif('34' in def_formation):
                                            prim_assigned = 'SLB'
                                    elif('Dime Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                case 'F Flat (0-4)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    elif('Nickel Personnel' in def_formation):
                                        if('43' in def_formation):
                                            prim_assigned = 'MLB'
                                        elif('34' in def_formation):
                                            prim_assigned = 'SLB'
                                    elif('Dime Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                case '0 Dig (0-4)':
                                    if ('43' in def_formation):
                                        if ('Nickel Personnel' in def_formation):
                                            prim_assigned = 'WLB'
                                        else:
                                            prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                            prim_assigned = 'SILB'
                                        elif ('Dime Personnel' in def_formation):                                    
                                            prim_assigned = 'SLB'
                                case '1 Out (5-8)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    elif('Nickel Personnel' in def_formation):
                                        if('43' in def_formation):
                                            prim_assigned = 'MLB'
                                        elif('34' in def_formation):
                                            prim_assigned = 'SLB'
                                    elif('Dime Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                case '2 Slant (5-8)':
                                    if ('43' in def_formation):
                                        if ('Nickel Personnel' in def_formation):
                                            prim_assigned = 'WLB'
                                        else:
                                            prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                            prim_assigned = 'SILB'
                                        elif ('Dime Personnel' in def_formation):                                    
                                            prim_assigned = 'SLB'
                                case '3 Comeback (9-12)':
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SLB'
                                    elif('Nickel Personnel' in def_formation):
                                        if('43' in def_formation):
                                            prim_assigned = 'MLB'
                                        elif('34' in def_formation):
                                            prim_assigned = 'SLB'
                                    elif('Dime Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                case '4 Curl (9-12)':
                                    if ('43' in def_formation):
                                        if ('Nickel Personnel' in def_formation):
                                            prim_assigned = 'WLB'
                                        else:
                                            prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                            prim_assigned = 'SILB'
                                        elif ('Dime Personnel' in def_formation):                                    
                                            prim_assigned = 'SLB'
                                case '5 Deep Out (13-18)':
                                    if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif('Dime Personnel' in def_formation):
                                        prim_assigned = 'DB'
                                case '6 Deep In (13-18)':
                                    prim_assigned = 'FS'
                                case '7 Corner (19-26)':
                                    if ('Regular' in def_formation or 'Nickel Personnel' in def_formation):
                                        prim_assigned = 'RCB'
                                    elif('Dime Personnel' in def_formation):
                                        prim_assigned = 'DB'
                                case '8 Post (19-26)':
                                    prim_assigned = 'SS'
                                case '9 Fade (27-39)':
                                    prim_assigned = 'SS'
                                case 'W Wheel (9-18)':
                                    prim_assigned = 'SS'
                                case 'D Deep Fade (40+)':
                                    prim_assigned = 'SS'
                    
                    elif position == 'RB':
                        if ('Man to Man' in def_formation or
                            'Cover-2' in def_formation or
                            'Cover-1' in def_formation or                              
                            'Press-2' in def_formation or
                            'Press-1' in def_formation or
                            'Tampa-2' in def_formation
                            ):                            
                            if ('43' in def_formation):
                                if 'Tampa-2' in def_formation:
                                    prim_assigned = ''
                                else:
                                    prim_assigned = 'MLB'
                            elif ('34' in def_formation):
                                if ('Weak' in off_formation):
                                    prim_assigned = 'WILB'
                                else:
                                    prim_assigned = 'SILB'                                    
                        elif ('Cover-3 Cloud' in def_formation):
                            if ('Weak' in off_formation):    
                                if route == 'S Screen (S)':
                                    if ('Dime'in def_formation):
                                        prim_assigned = 'WLB'
                                    else:
                                        prim_assigned = 'NB'
                                elif route == 'F Flat (0-4)':
                                    if route == 'S Screen (S)':
                                        if ('Dime'in def_formation):
                                            prim_assigned = 'WLB'
                                        else:
                                            prim_assigned = 'NB'                               
                                elif route == '0 Dig (0-4)':                                     
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'                                    
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'WLB'                            
                                        elif ('Nickel' in def_formation):
                                            prim_assigned = 'SILB'
                                        elif ('Regular' in def_formation):
                                            prim_assigned = 'WILB'
                                elif route == '1 Out (5-8)':
                                    if ('Dime'in def_formation):
                                        prim_assigned = 'WLB'
                                    else:
                                        prim_assigned = 'NB'                                 
                                elif route == '2 Slant (5-8)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'                                    
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'WLB'                            
                                        elif ('Nickel' in def_formation):
                                            prim_assigned = 'SILB'
                                        elif ('Regular' in def_formation):
                                            prim_assigned = 'WILB'                                         
                                elif route == '3 Comeback (9-12)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'                                    
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'WLB'                            
                                        elif ('Nickel' in def_formation):
                                            prim_assigned = 'SILB'
                                        elif ('Regular' in def_formation):
                                            prim_assigned = 'WILB'                                   
                                elif route == '4 Curl (9-12)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'                                    
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'WLB'                            
                                        elif ('Nickel' in def_formation):
                                            prim_assigned = 'SILB'
                                        elif ('Regular' in def_formation):
                                            prim_assigned = 'WILB'
                                elif route == 'W Wheel (9-18)':
                                    if ('Dime'in def_formation):
                                        prim_assigned = 'WLB'
                                    else:
                                        prim_assigned = 'NB'
                            else:    
                                if route == 'S Screen (S)':
                                    if ('Regular'in def_formation):
                                        prim_assigned = 'SLB'
                                    else:
                                        prim_assigned = 'RCB'
                                elif route == 'F Flat (0-4)':
                                    if ('Regular'in def_formation):
                                        prim_assigned = 'SLB'
                                    else:
                                        prim_assigned = 'RCB'                               
                                elif route == '0 Dig (0-4)':                                     
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'                                    
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'SLB'                            
                                        elif ('Nickel' in def_formation):
                                            prim_assigned = 'SLB'
                                        elif ('Regular' in def_formation):
                                            prim_assigned = 'SILB'
                                elif route == '1 Out (5-8)':
                                    if ('Regular'in def_formation):
                                        prim_assigned = 'SLB'
                                    else:
                                        prim_assigned = 'RCB'                                 
                                elif route == '2 Slant (5-8)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'                                    
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'SLB'                            
                                        elif ('Nickel' in def_formation):
                                            prim_assigned = 'SLB'
                                        elif ('Regular' in def_formation):
                                            prim_assigned = 'SILB'                                         
                                elif route == '3 Comeback (9-12)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'                                    
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'SLB'                            
                                        elif ('Nickel' in def_formation):
                                            prim_assigned = 'SLB'
                                        elif ('Regular' in def_formation):
                                            prim_assigned = 'SILB'                                   
                                elif route == '4 Curl (9-12)':
                                    if ('43' in def_formation):
                                        prim_assigned = 'MLB'                                    
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'SLB'                            
                                        elif ('Nickel' in def_formation):
                                            prim_assigned = 'SLB'
                                        elif ('Regular' in def_formation):
                                            prim_assigned = 'SILB'
                                elif route == 'W Wheel (9-18)':
                                    if ('Regular'in def_formation):
                                        prim_assigned = 'SLB'
                                    else:
                                        prim_assigned = 'RCB'
                        elif ('Cover-3 Sky' in def_formation):
                            if ('Weak' in off_formation):    
                                if route == 'S Screen (S)':
                                    if ('Regular'in def_formation):
                                        prim_assigned = 'WLB'
                                    else:
                                        prim_assigned = 'LCB'
                                elif route == 'F Flat (0-4)':
                                    if route == 'S Screen (S)':
                                        if ('Regular'in def_formation):
                                            prim_assigned = 'WLB'
                                        else:
                                            prim_assigned = 'LCB'                               
                                elif route == '0 Dig (0-4)':                                     
                                    if ('43' in def_formation):
                                        if ('Nickel' in def_formation):
                                            prim_assigned = 'WLB'
                                        else:
                                            prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'WILB'                            
                                        else:
                                            prim_assigned = 'WLB'                                        
                                elif route == '1 Out (5-8)':
                                    if route == 'S Screen (S)':
                                        if ('Regular'in def_formation):
                                            prim_assigned = 'WLB'
                                        else:
                                            prim_assigned = 'LCB'                                 
                                elif route == '2 Slant (5-8)':
                                    if ('43' in def_formation):
                                        if ('Nickel' in def_formation):
                                            prim_assigned = 'WLB'
                                        else:
                                            prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'WILB'                            
                                        else:
                                            prim_assigned = 'WLB'                                         
                                elif route == '3 Comeback (9-12)':
                                    if ('43' in def_formation):
                                        if ('Nickel' in def_formation):
                                            prim_assigned = 'WLB'
                                        else:
                                            prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'WILB'                            
                                        else:
                                            prim_assigned = 'WLB'                                  
                                elif route == '4 Curl (9-12)':
                                    if ('43' in def_formation):
                                        if ('Nickel' in def_formation):
                                            prim_assigned = 'WLB'
                                        else:
                                            prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'WILB'                            
                                        else:
                                            prim_assigned = 'WLB'
                                elif route == 'W Wheel (9-18)':
                                    if route == 'S Screen (S)':
                                        if ('Regular'in def_formation):
                                            prim_assigned = 'WLB'
                                        else:
                                            prim_assigned = 'LCB'
                            else:    
                                if route == 'S Screen (S)':
                                    if ('43' in def_formation):                                        
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'SLB'
                                        elif ('Nickel' in def_formation):
                                            prim_assigned = 'SS'
                                        elif ('Dime' in def_formation):
                                            prim_assigned = 'RCB'
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'RCB'
                                        else:
                                            prim_assigned = 'SLB'                                        
                                elif route == 'F Flat (0-4)':
                                    if ('43' in def_formation):                                        
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'SLB'
                                        elif ('Nickel' in def_formation):
                                            prim_assigned = 'SS'
                                        elif ('Dime' in def_formation):
                                            prim_assigned = 'RCB'
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'RCB'
                                        else:
                                            prim_assigned = 'SLB'                               
                                elif route == '0 Dig (0-4)':                                     
                                    if ('43' in def_formation):
                                        if ('Nickel' in def_formation):
                                            prim_assigned = 'MLB'
                                        else:
                                            prim_assigned = 'SS'
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'SLB'                            
                                        else:
                                            prim_assigned = 'SS'
                                elif route == '1 Out (5-8)':
                                    if ('43' in def_formation):                                        
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'SLB'
                                        elif ('Nickel' in def_formation):
                                            prim_assigned = 'SS'
                                        elif ('Dime' in def_formation):
                                            prim_assigned = 'RCB'
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'RCB'
                                        else:
                                            prim_assigned = 'SLB'                                
                                elif route == '2 Slant (5-8)':
                                    if ('43' in def_formation):
                                        if ('Nickel' in def_formation):
                                            prim_assigned = 'MLB'
                                        else:
                                            prim_assigned = 'SS'
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'SLB'                            
                                        else:
                                            prim_assigned = 'SS'
                                elif route == '3 Comeback (9-12)':
                                    if ('43' in def_formation):
                                        if ('Nickel' in def_formation):
                                            prim_assigned = 'MLB'
                                        else:
                                            prim_assigned = 'SS'
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'SLB'                            
                                        else:
                                            prim_assigned = 'SS'                                   
                                elif route == '4 Curl (9-12)':
                                    if ('43' in def_formation):
                                        if ('Nickel' in def_formation):
                                            prim_assigned = 'MLB'
                                        else:
                                            prim_assigned = 'SS'
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'SLB'                            
                                        else:
                                            prim_assigned = 'SS'
                                elif route == 'W Wheel (9-18)':
                                    if ('43' in def_formation):                                        
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'SLB'
                                        elif ('Nickel' in def_formation):
                                            prim_assigned = 'SS'
                                        elif ('Dime' in def_formation):
                                            prim_assigned = 'RCB'
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'RCB'
                                        else:
                                            prim_assigned = 'SLB'                                                                       
                        elif ('Cover-4' in def_formation):
                            if ('Weak' in off_formation):    
                                if route == 'S Screen (S)':
                                    if ('Regular'in def_formation):
                                        prim_assigned = 'WLB'
                                    else:
                                        prim_assigned = 'LCB'
                                elif route == 'F Flat (0-4)':
                                    if route == 'S Screen (S)':
                                        if ('Regular'in def_formation):
                                            prim_assigned = 'WLB'
                                        else:
                                            prim_assigned = 'LCB'                               
                                elif route == '0 Dig (0-4)':                                     
                                    if ('43' in def_formation):
                                        if ('Nickel' in def_formation):
                                            prim_assigned = 'WLB'
                                        else:
                                            prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'WILB'                            
                                        else:
                                            prim_assigned = 'WLB'                                        
                                elif route == '1 Out (5-8)':
                                    if route == 'S Screen (S)':
                                        if ('Regular'in def_formation):
                                            prim_assigned = 'WLB'
                                        else:
                                            prim_assigned = 'LCB'                                 
                                elif route == '2 Slant (5-8)':
                                    if ('43' in def_formation):
                                        if ('Nickel' in def_formation):
                                            prim_assigned = 'WLB'
                                        else:
                                            prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'WILB'                            
                                        else:
                                            prim_assigned = 'WLB'                                         
                                elif route == '3 Comeback (9-12)':
                                    if ('43' in def_formation):
                                        if ('Nickel' in def_formation):
                                            prim_assigned = 'WLB'
                                        else:
                                            prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'WILB'                            
                                        else:
                                            prim_assigned = 'WLB'                                  
                                elif route == '4 Curl (9-12)':
                                    if ('43' in def_formation):
                                        if ('Nickel' in def_formation):
                                            prim_assigned = 'WLB'
                                        else:
                                            prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'WILB'                            
                                        else:
                                            prim_assigned = 'WLB'
                                elif route == 'W Wheel (9-18)':
                                    if route == 'S Screen (S)':
                                        if ('Regular'in def_formation):
                                            prim_assigned = 'WLB'
                                        else:
                                            prim_assigned = 'LCB'
                            else:    
                                if route == 'S Screen (S)':
                                    if ('43' in def_formation):                                        
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'SLB'
                                        elif ('Nickel' in def_formation):
                                            prim_assigned = 'MLB'
                                        elif ('Dime' in def_formation):
                                            prim_assigned = 'RCB'
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'RCB'
                                        else:
                                            prim_assigned = 'SLB'                                        
                                elif route == 'F Flat (0-4)':
                                    if ('43' in def_formation):                                        
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'SLB'
                                        elif ('Nickel' in def_formation):
                                            prim_assigned = 'MLB'
                                        elif ('Dime' in def_formation):
                                            prim_assigned = 'RCB'
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'RCB'
                                        else:
                                            prim_assigned = 'SLB'                               
                                elif route == '0 Dig (0-4)':                                     
                                    if ('43' in def_formation):
                                        if ('Nickel' in def_formation):
                                            prim_assigned = 'WLB'
                                        else:
                                            prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'SLB'                            
                                        else:
                                            prim_assigned = 'SILB'
                                elif route == '1 Out (5-8)':
                                    if ('43' in def_formation):                                        
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'SLB'
                                        elif ('Nickel' in def_formation):
                                            prim_assigned = 'MLB'
                                        elif ('Dime' in def_formation):
                                            prim_assigned = 'RCB'
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'RCB'
                                        else:
                                            prim_assigned = 'SLB'                                
                                elif route == '2 Slant (5-8)':
                                    if ('43' in def_formation):
                                        if ('Nickel' in def_formation):
                                            prim_assigned = 'WLB'
                                        else:
                                            prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'SLB'                            
                                        else:
                                            prim_assigned = 'SILB'
                                elif route == '3 Comeback (9-12)':
                                    if ('43' in def_formation):
                                        if ('Nickel' in def_formation):
                                            prim_assigned = 'WLB'
                                        else:
                                            prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'SLB'                            
                                        else:
                                            prim_assigned = 'SILB'                                   
                                elif route == '4 Curl (9-12)':
                                    if ('43' in def_formation):
                                        if ('Nickel' in def_formation):
                                            prim_assigned = 'WLB'
                                        else:
                                            prim_assigned = 'MLB'
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'SLB'                            
                                        else:
                                            prim_assigned = 'SILB'
                                elif route == 'W Wheel (9-18)':
                                    if ('43' in def_formation):                                        
                                        if ('Regular' in def_formation):
                                            prim_assigned = 'SLB'
                                        elif ('Nickel' in def_formation):
                                            prim_assigned = 'MLB'
                                        elif ('Dime' in def_formation):
                                            prim_assigned = 'RCB'
                                    elif ('34' in def_formation):
                                        if ('Dime' in def_formation):
                                            prim_assigned = 'RCB'
                                        else:
                                            prim_assigned = 'SLB'
                        
                    elif position == 'FB':
                        if ('Man to Man' in def_formation or
                            'Cover-2' in def_formation or
                            'Cover-1' in def_formation or                              
                            'Press-2' in def_formation or
                            'Press-1' in def_formation or
                            'Tampa-2' in def_formation
                            ):                            
                            prim_assigned = 'SLB'                                    
                        elif ('Cover-3 Cloud' in def_formation):
                            if ('43'in def_formation):
                                prim_assigned = 'MLB'
                            else:
                                if ('Pro' in off_formation):
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'SILB'
                                    else:
                                        prim_assigned = 'SLB'
                                else:
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'WILB'
                                    elif ('Nickel' in def_formation):
                                        prim_assigned = 'SILB'
                                    elif ('Dime' in def_formation):
                                        prim_assigned = 'WLB'                                                     
                        elif ('Cover-3 Sky' in def_formation):
                            if ('34'in def_formation):
                                if ('Dime' in def_formation):
                                    prim_assigned = 'SS'
                                else:
                                    prim_assigned = 'SILB'
                            else:
                                if ('Pro' in off_formation):
                                    if ('Nickel' in def_formation):
                                        prim_assigned = 'MLB'
                                    else:
                                        prim_assigned = 'SS'
                                else:
                                    if ('Nickel' in def_formation):
                                        prim_assigned = 'WLB'
                                    else:
                                        prim_assigned = 'MLB'                                                                                                   
                        elif ('Cover-4' in def_formation):
                            if ('43'in def_formation):
                                if ('Nickel' in def_formation):
                                    prim_assigned = 'WLB'
                                else:
                                    prim_assigned = 'MLB'
                            else:
                                if ('Pro' in off_formation):
                                    if ('Dime' in def_formation):
                                        prim_assigned = 'SLB'
                                    else:
                                        prim_assigned = 'SILB'
                                else:
                                    if ('Regular' in def_formation):
                                        prim_assigned = 'WILB'
                                    else:
                                        prim_assigned = 'WLB'                                    
                    
                    print("Assigned defender is", prim_assigned)
                    prim_defender = defensive_play_personnel[defensive_play_personnel['Position'].str.startswith(str(prim_assigned))]
                    prim_def_name = prim_defender['Player'].iloc[0]
                    prim_coverage_type = prim_defender['Assignment'].iloc[0]
                    print(prim_def_name, "was in", prim_coverage_type, "coverage")
                    
                    print("Receiver was", position)
                    print("Route was", route)
                    print("Defensive formation was", def_formation)
                    print("Offensive formation was", off_formation)
                    
                    if 'completed' in play_result:
                        caught = 1
                        rec_yards = int(play_result_arr[12])
                        yards_after_catch = 0
                        if 'after the catch' in play_result:
                            words = play_result.split()
                            index_after = words.index("after")
                            yards_after_catch = int(words[index_after - 2])
   
    #             new_rec_row = []
    #             new_rec_row.append(receiver_name)
    #             new_rec_row.append(position)
    #             new_rec_row.append(priority)
    #             new_rec_row.append(route)
    #             new_rec_row.append(targeted)
    #             new_rec_row.append(caught)
    #             new_rec_row.append(rec_yards)
    #             new_rec_row.append(yards_after_catch)
    #             new_rec_row.append(passer)
    #             receivers.append(new_rec_row)
        
    #     csv_file = 'receivers_in_game.csv'
    #     file_exists = os.path.isfile(csv_file)

    #     try:
    #         with open(csv_file, 'a', newline='') as csvfile:
    #             writer = csv.writer(csvfile)
    #             if not file_exists:
    #                 writer.writerow(['Player Name','Position' ,'Route Prioity', 'Route', 'Targeted?', 'Caught?', 'Yards', 'YAC', 'Passer'])
    #             writer.writerows(receivers)
    #             output_text = f"Receiver data for this play appended to '{csv_file}'."
    #             output_widget.append(output_text)
    #     except Exception as e:
    #         output_text = f"Error writing to CSV file '{csv_file}': {e}"
    #         output_widget.append(output_text)
        return pass_defenders