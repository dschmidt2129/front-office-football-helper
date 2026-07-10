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
import re

class game_service:

    def __init__(self, path, output_widget):
        # initializing player_service and team_service
        self.ps = ps(path)
        self.ts = ts(path)
        self.cleaned_game_log = None      # cached cleaned log
        self._all_tables = None           # cached tables from the html file

    def _load_all_tables(self, path):
        """read_html only once per invocation of the service."""
        if self._all_tables is None:
            fname = self.read_game_log(path)
            with open(fname, 'rb') as f:          # make sure the handle is closed
                self._all_tables = pd.read_html(f, keep_default_na=False)
        return self._all_tables

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
               'won the coin toss' in play or
               'Final Score' in play or
               'False Start' in play or
               'Informal' in play or
               'dropped to one knee' in play or
               'spiked the ball' in play or
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
    
    def get_offensive_play_personnel(self, index, path):
        # Returns the offensive play personnel from the indexed play result from the game logs
        tables = self._load_all_tables(path)
        try:
            return tables[index + 1].iloc[:, 0:3]
        except IndexError:
            print(f"No offensive play personnel found for index {index+1}")
            return None
    
    def get_defensive_play_personnel(self, index, path):
        # Returns the defensive play personnel from the indexed play result from the game logs
        tables = self._load_all_tables(path)
        try:
            return tables[index + 1].iloc[:, 3:6]
        except IndexError:
            print(f"No defensive play personnel found for index {index+1}")
            return None

    def get_player_name_from_play(self, play):
        # look for “Firstname Lastname pass” / “Firstname Lastname ran” / …
        m = re.search(r'([A-Z][a-z]+ [A-Z][a-z]+) (?:pass|run|sacked|scrambled|kneels)', play)
        if m:
            return m.group(1)
        # fallback to the old split-based approach
        parts = play.split()
        if len(parts) >= 5:
            return parts[3] + ' ' + parts[4]
        return ''

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
            
        player_name = self.get_player_name_from_play(play_result)
        output_text = f"Player name extracted from play result: {player_name}"

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
                if ('pass' in play_result or
                    'fell incomplete' in play_result or
                    'completed' in play_result or
                    'intercepted' in play_result or
                    'was thrown incomplete' in play_result or
                    'was blocked at the line' in play_result or
                    'sacked' in play_result or
                    'hurried' in play_result
                    ):
                    normalized_defensive_personnel = self.normalize_defensive_play_personnel(defensive_play_personnel.copy())
                    self.write_pass_rush_success_rate(normalized_defensive_personnel, formation, play_result, output_widget)
                if ('fell incomplete' in play_result or
                    'completed' in play_result or
                    'intercepted' in play_result or
                    'was thrown incomplete' in play_result or
                    'was blocked at the line' in play_result
                    ):
                    offensive_play_personnel = self.get_offensive_play_personnel(index, path)                    
                    pass_defenders_in_play = self.get_pass_defenders_from_play(formation, play_result, defensive_play_personnel, output_widget, offensive_play_personnel)
                    output_text = str(pass_defenders_in_play)
                    output_widget.append(output_text)
                    QApplication.processEvents() # this should allow the application to update real time
                    # todo: update for pass rush defenders here
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
        for i in range(len(offensive_play_personnel)):
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
                self.write_receiver_pivot_summary(csv_file, output_widget)
        except Exception as e:
            output_text = f"Error writing to CSV file '{csv_file}': {e}"
            output_widget.append(output_text)
            QApplication.processEvents() # this should allow the application to update real time
        return receivers

    def write_receiver_pivot_summary(self, receivers_csv_file, output_widget):
        """Writes a second spreadsheet with pivot-style receiver efficiency summaries."""
        summary_csv_file = 'receivers_pivot_summary.csv'
        try:
            if not os.path.isfile(receivers_csv_file):
                output_widget.append(f"Cannot create pivot summary. Missing '{receivers_csv_file}'.")
                QApplication.processEvents()
                return

            receivers_df = pd.read_csv(receivers_csv_file)
            if receivers_df.empty:
                output_widget.append("Cannot create pivot summary. Receiver CSV is empty.")
                QApplication.processEvents()
                return

            # Ensure expected numeric columns are numeric before aggregations.
            receivers_df['Yards'] = pd.to_numeric(receivers_df['Yards'], errors='coerce').fillna(0)
            receivers_df['Caught?'] = pd.to_numeric(receivers_df['Caught?'], errors='coerce').fillna(0)

            # Pivot 1: yards per reception by receiver.
            ypr_pivot = pd.pivot_table(
                receivers_df,
                index=['Player Name'],
                values=['Yards', 'Caught?'],
                aggfunc='sum',
                fill_value=0
            ).reset_index()
            ypr_pivot['Yards/Reception'] = ypr_pivot.apply(
                lambda row: round(row['Yards'] / row['Caught?'], 2) if row['Caught?'] > 0 else 0,
                axis=1
            )
            ypr_pivot = ypr_pivot[['Player Name', 'Yards', 'Caught?', 'Yards/Reception']]
            ypr_pivot = ypr_pivot.rename(columns={
                'Yards': 'Total Receiving Yards',
                'Caught?': 'Total Receptions',
                'Yards/Reception': 'Yards Per Reception'
            })

            # Pivot 2: yards per route run by receiver.
            yprr_pivot = pd.pivot_table(
                receivers_df,
                index=['Player Name'],
                values=['Yards', 'Route'],
                aggfunc={'Yards': 'sum', 'Route': 'count'},
                fill_value=0
            ).reset_index()
            yprr_pivot = yprr_pivot.rename(columns={'Route': 'Total Routes Run', 'Yards': 'Total Receiving Yards'})
            yprr_pivot['Yards Per Route Run'] = yprr_pivot.apply(
                lambda row: round(row['Total Receiving Yards'] / row['Total Routes Run'], 2) if row['Total Routes Run'] > 0 else 0,
                axis=1
            )
            yprr_pivot = yprr_pivot[['Player Name', 'Total Receiving Yards', 'Total Routes Run', 'Yards Per Route Run']]

            with open(summary_csv_file, 'w', newline='') as csvfile:
                csvfile.write('Pivot Table - Yards Per Reception\n')
                ypr_pivot.to_csv(csvfile, index=False, header=True)
                csvfile.write('\n')
                csvfile.write('Pivot Table - Yards Per Route Run\n')
                yprr_pivot.to_csv(csvfile, index=False, header=True)

            output_widget.append(
                f"Receiver pivot summary updated in '{summary_csv_file}' (Yards Per Reception and Yards Per Route Run)."
            )
            QApplication.processEvents()
        except Exception as e:
            output_widget.append(f"Error creating receiver pivot summary '{summary_csv_file}': {e}")
            QApplication.processEvents()
    
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

    def normalize_defensive_play_personnel(self, defensive_play_personnel):
        defensive_play_personnel.columns = ['Position_Player', 'Assignment', 'Rating']
        defensive_play_personnel[['Position', 'Player']] = defensive_play_personnel['Position_Player'].str.split(' ', n=1, expand=True)
        defensive_play_personnel = defensive_play_personnel.drop(columns=['Position_Player'])
        defensive_play_personnel = defensive_play_personnel[['Position', 'Player', 'Assignment', 'Rating']]
        defensive_play_personnel['Position'] = defensive_play_personnel['Position'].astype(str).str.strip()
        defensive_play_personnel['Player'] = defensive_play_personnel['Player'].astype(str).str.strip()
        defensive_play_personnel['Assignment'] = defensive_play_personnel['Assignment'].astype(str).str.strip()
        return defensive_play_personnel

    def write_pass_rush_success_rate(self, defensive_play_personnel, def_formation, play_result, output_widget):
        pass_rush_success = int('sacked' in play_result or 'hurried' in play_result)
        pass_rush_rows = []

        for _, defender_row in defensive_play_personnel.iterrows():
            assignment = str(defender_row['Assignment']).strip()
            if assignment not in ('Rush Passer', 'Blitz Passer'):
                continue
            pass_rush_rows.append([
                str(defender_row['Player']).strip(),
                str(defender_row['Position']).strip(),
                assignment,
                str(def_formation).strip(),
                int(assignment == 'Blitz Passer'),
                pass_rush_success
            ])

        if not pass_rush_rows:
            return

        csv_file = 'pass_rush_success_rate.csv'
        file_exists = os.path.isfile(csv_file)

        try:
            with open(csv_file, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                if not file_exists:
                    writer.writerow(['Defender Name', 'Defender Position', 'Defense Coverage', 'Formation/Coverage', 'Blitz', 'Pass Rush Success'])
                writer.writerows(pass_rush_rows)
                output_widget.append(f"Pass rush success data for this play appended to '{csv_file}'.")
                QApplication.processEvents() # this should allow the application to update real time
        except Exception as e:
            output_widget.append(f"Error writing to CSV file '{csv_file}': {e}")
            QApplication.processEvents() # this should allow the application to update real time
    
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

        defensive_play_personnel = self.normalize_defensive_play_personnel(defensive_play_personnel)
        
        Num_TE = 0
        Num_Slot = 0
        
        if 'fell incomplete' in play_result:
            intended_receiver_last_name = (play_result_arr[12])
            intended_receiver_last_name = intended_receiver_last_name[:-1]            
        elif 'completed' in play_result:
            intended_receiver_last_name = (play_result_arr[10])
        elif 'intercepted' in play_result:
            intended_receiver_last_name = (play_result_arr[11])
        elif 'was thrown incomplete' in play_result:
            intended_receiver_last_name = (play_result_arr[13])
            intended_receiver_last_name = intended_receiver_last_name[:-1]
        elif 'was blocked at the line' in play_result:
            intended_receiver_last_name = (play_result_arr[15])
            intended_receiver_last_name = intended_receiver_last_name[:-1]

        for i in range(1, len(offensive_play_personnel)):
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
                    prim_coverage_type = ''
                    doub_coverage_type = ''
                    explicit_double_found = False

                    # Handle explicit traditional doubles from the play table, e.g. "Double X(SE)".
                    explicit_double_label = f"Double {position}"
                    explicit_double_row = defensive_play_personnel[
                        defensive_play_personnel['Assignment'] == explicit_double_label
                    ]
                    if explicit_double_row.empty:
                        explicit_double_row = defensive_play_personnel[
                            defensive_play_personnel['Assignment'].str.contains(explicit_double_label, case=False, regex=False)
                        ]
                    if not explicit_double_row.empty:
                        doub_assigned = str(explicit_double_row['Position'].iloc[0])
                        doub_def_name = str(explicit_double_row['Player'].iloc[0])
                        # doub_coverage_type = str(explicit_double_row['Assignment'].iloc[0])
                        doub_coverage_type = 'Double Coverage Receiver' # changing to double coverage receiver due to not caring if it is x or y or slot, just that it is a double team on the receiver
                        explicit_double_found = True
                        output_widget.append(
                            f"Explicit double coverage found: {doub_coverage_type} by {doub_assigned} {doub_def_name}"
                        )
                        QApplication.processEvents() # this should allow the application to update real time

                    if prim_assigned is not None:
                        try:
                            defender_row = defensive_play_personnel[defensive_play_personnel['Position'] == prim_assigned]
                            if not defender_row.empty:
                                prim_def_name = str(defender_row['Player'].iloc[0])
                                print("Primary defender is", prim_def_name)
                                prim_coverage_type = str(defender_row['Assignment'].iloc[0])
                                print("Primary coverage type is", prim_coverage_type)
                                pass_defenders.append(defender_row)
                                QApplication.processEvents() # this should allow the application to update real time
                            else:
                                output_widget.append(f"No defender found for assigned position {prim_assigned}")
                                QApplication.processEvents() # this should allow the application to update real time
                        except (IndexError, ValueError, TypeError) as e:
                            print("Error finding primary defender:", e)
                            prim_def_name = ''

                        if doub_assigned is not None and not explicit_double_found:
                            try:
                                defender_row = defensive_play_personnel[defensive_play_personnel['Position'] == doub_assigned]
                                if not defender_row.empty:
                                    doub_def_name = str(defender_row['Player'].iloc[0])
                                    doub_coverage_type = str(defender_row['Assignment'].iloc[0])
                            except (IndexError, ValueError, TypeError) as e:
                                print("Error finding double team defender:", e)
                                doub_def_name = ''

                        if doub_coverage_type == 'Blitz Passer':
                            doub_assigned = ''
                            doub_def_name = ''
                            doub_coverage_type = ''
                    
                        if prim_coverage_type == 'Blitz Passer':
                                if doub_assigned != '':
                                    prim_assigned = doub_assigned
                                    prim_def_name = doub_def_name
                                    prim_coverage_type = doub_coverage_type
                                    doub_assigned = ''
                                    doub_def_name = ''
                                    doub_coverage_type = ''
                                else:
                                    prim_assigned = ''
                                    prim_def_name = ''
                        result = {
                            "assigned_position": prim_assigned,
                            "defender_name": prim_def_name,
                            "coverage_type": prim_coverage_type,
                            "receiver_position": position,
                            "route": route,
                            "def_formation": def_formation,
                            "off_formation": off_formation
                        }

                        pass_defenders.append(result)
                        output_widget.append(
                            f"Primary defender: {prim_def_name} ({prim_assigned}), Coverage: {prim_coverage_type}, "
                            f"Receiver: {position}, Route: {route}, Def: {def_formation}, Off: {off_formation}"
                        )
                        QApplication.processEvents() # this should allow the application to update real time
                    else:
                        output_widget.append(f"No primary defender found for assigned position {prim_assigned}")
                        QApplication.processEvents() # this should allow the application to update real time

                    QApplication.processEvents() # this should allow the application to update real time
                    print('Pass Defenders Array', pass_defenders)
                    print("Receiver was", position)

                    if 'completed' in play_result:
                        caught = 1
                        rec_yards = int(play_result_arr[12])
                        yards_after_catch = 0
                        if 'after the catch' in play_result:
                            words = play_result.split()
                            index_after = words.index("after")
                            yards_after_catch = int(words[index_after - 2])
                    else:
                        caught = 0
                        rec_yards = 0
                        yards_after_catch = 0

                    new_pass_def_row = []
                    new_pass_def_row.append(prim_def_name)
                    new_pass_def_row.append(prim_assigned)             
                    new_pass_def_row.append(position)
                    new_pass_def_row.append(route)
                    new_pass_def_row.append(prim_coverage_type)
                    new_pass_def_row.append(def_formation)
                    new_pass_def_row.append(caught)
                    new_pass_def_row.append(rec_yards)
                    new_pass_def_row.append(yards_after_catch)
                    new_pass_def_row.append(doub_assigned)
                    new_pass_def_row.append(doub_def_name)
                    new_pass_def_row.append(doub_coverage_type)
                    pass_def.append(new_pass_def_row)

                    csv_file = 'pass_def_in_game.csv'
                    file_exists = os.path.isfile(csv_file)

                    try:
                        with open(csv_file, 'a', newline='') as csvfile:
                            writer = csv.writer(csvfile)
                            if not file_exists:
                                writer.writerow(['Player Name','Position' ,'Receiver', 'Route', 'Coverage', 'Formation', 'Caught?', 'Yards', 'YAC', 'DC Position', 'DC Player Name', 'DC Coverage'])
                            writer.writerows(pass_def)
                            output_text = f"Pass defender data for this play appended to '{csv_file}'."
                            output_widget.append(output_text)
                            QApplication.processEvents() # this should allow the application to update real time
                    except Exception as e:
                        output_text = f"Error writing to CSV file '{csv_file}': {e}"
                        output_widget.append(output_text)
                        QApplication.processEvents() # this should allow the application to update real time
                    return pass_defenders
