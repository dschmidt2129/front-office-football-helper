import pandas as pd

class FileReader:
    def __init__(self):
        # no variables need initialized
        pass

    def get_game_log(self, file_name):
        # grabs the game log from the local game file system
        file = open(file_name)
        return file
    
    def read_game_log(self):
        # returns the file name from the local file system when retrieved from the game
        file = self.get_game_log('C:/Users/david/AppData/Local/Solecismic Software/Front Office Football Eight/leagues/SFL00004/lastboxlog.html')
        return (file.name)

    def get_roster(self):
        # retrieves the roster from the game logs so that the stats can be compiled
        file = self.get_game_log(self.read_game_log())
        all_tables = pd.read_html(file)
        return all_tables[151]

    def get_play_result(self, index):
        # returns the indexed play result from the logs
        # todo will need to split the table to determine which side to grab the result set from
        # write this to file to see the full result set
        file = self.get_game_log(self.read_game_log())
        all_tables = pd.read_html(file, keep_default_na=False)
        return all_tables[index]

    def get_team_results(self):
        start_index = 1 # index of the table that is the first play result data
        roster_table_index = 151 # this is the table index value that holds our team rosters
        for i in range (start_index, roster_table_index):
            print(i)