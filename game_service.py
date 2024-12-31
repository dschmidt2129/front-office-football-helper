import pandas as pd

class game_service:

    def __init__(self):
        # no variables initialized
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
        # returns the indexed play result from the game logs
        file = self.get_game_log(self.read_game_log())
        all_tables = pd.read_html(file, keep_default_na=False)
        print("number of tables: " + str(len(all_tables)))
        # todo: need to find the text for the play result
        # the first play always starts at index 3
        print(all_tables[1])
        return all_tables[index]

    def get_play_result(self, index):
        # returns the play result from the game logs
        file = self.get_game_log(self.read_game_log())
        # index 0 is a list of the all of the play results
