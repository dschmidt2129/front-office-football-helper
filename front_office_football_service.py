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
        length = len(all_tables)-1
        return all_tables[length]

    def get_play_result(self, index):
        # returns the indexed play result from the logs
        file = self.get_game_log(self.read_game_log())
        all_tables = pd.read_html(file, keep_default_na=False)
        return all_tables[index]

    def get_player_pos(self, list):
        pos = ''
        player = list[1] # get the first player in the list to check if the player is on the roster
        pos = player[0:2]
        print('position: ' + pos)
        if('(' in pos):
            # handles the wide receiver specialized positions
            pos = player[0:5]
            print('position: ' + pos)
        return pos
    
    def get_player_name_from_play(self, play_result):
        pass
