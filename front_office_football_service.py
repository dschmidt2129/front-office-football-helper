import pandas as pd

class FileReader:
    # todo: need to completely refactor this class because it is completely muddled with too much varied functionality
    def __init__(self):
        # no variables need initialized
        pass

    # function to return the team id from the team_information.csv file 
    def get_team_info(self, team):
        # cleveland is team id 30
        # las vegas is team id 20
        # miami is team id 14
        # indianapolis is team id 11
        # todo: update this file location to the game file location. 
        # todo: may need to have the users upload this file at each run? not sure how often this file changes
        team_info = pd.read_csv("resources/team_information.csv")
        print(team_info)
        team_id = -1
        # switch statement to return team id
        match team:
            case 'Cleveland':
                team_id = team_info.iat[30,0]
                print('Cleveland team id: ' + str(team_id))
                return team_id
            case 'Las Vegas':
                team_id = team_info.iat[20,0]
                print('Las Vegas team id: ' + str(team_id))
                return team_id
            case 'Miami':
                team_id = team_info.iat[14,0]
                print('Miami team id: ' + str(team_id))
                return team_id
            case 'Indianapolis':
                team_id = team_info.iat[11,0]
                print('Indianapolis team id: ' + str(team_id))
                return team_id
            case _:
                print("No team passed!!")
                return team_id

    def get_game_log(self, file_name):
        # grabs the game log from the local game file system
        file = open(file_name)
        return file
    
    def read_game_log(self):
        # returns the file name from the local file system when retrieved from the game
        file = self.get_game_log('resources/lastboxlog.html')
        return (file.name)

    def get_roster(self):
        # retrieves the roster from the game logs so that the stats can be compiled
        # should read from player_record.csv and find the matching player and team ids from another file
        # can match player id with the id in player_information.csv
        # can match team id with the id in team_information.csv
        # todo: still need to add csv files to resources directory
        file = self.get_game_log(self.read_game_log())
        all_tables = pd.read_html(file)
        length = len(all_tables)-1
        return all_tables[length]

    def get_play_result(self, index):
        # returns the indexed play result from the logs
        file = self.get_game_log(self.read_game_log())
        all_tables = pd.read_html(file, keep_default_na=False)
        return all_tables[index]

    def get_player_pos(self, list, index):
        # returns the player position - will be used to confirm the last name on the roster
        pos = ''
        player = list[index] # get the first player in the list to check if the player is on the roster
        pos = player[0:2]
        print('position: ' + pos)
        if('(' in pos):
            # handles the wide receiver specialized positions
            pos = player[0:5]
            print('position: ' + pos)
        return pos
    
    def get_player_name_from_play(self):
        play_result = self.get_play_result(1)
        player = play_result.iat[1,0] # first player in the play result on the left hand side table
        if player[0:2] == 'QB':
            print("qb")
        # player_pos = self.get_player_pos()
        print ("player pos : " + "player name : ")
