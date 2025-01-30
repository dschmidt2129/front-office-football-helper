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
        play_result = plays.loc[index+3,0]
        play_result = play_result.split('OFFENSE')[0] # taking only the play result from the converted panda substring
        # print(play_result)
        return play_result

    def get_player_performance_from_play(self, index, player_index, is_offense):
        # todo: call this method when determining if the player is on the active roster
        # gets the player's performance and actions from the play +, -, etc...
        play_result = self.get_play_result(index) # for whatever reason, the html table isn't indexed like an array or list when converted to a dataframe
        print(play_result)
        if(is_offense):
            offensive_play_personnel = self.get_offensive_play_personnel(index)
            # print(offensive_play_personnel)
            # quarterback and offensive line are special cases where they don't have a play result and qb will return *** instead of +,-
            player = offensive_play_personnel.iloc[player_index]
            print(player)
            return player
        else:
           defensive_play_personnel = self.get_defensive_play_personnel(index)
        #    print(defensive_play_personnel)
           player = defensive_play_personnel.iloc[player_index]
           print(player)
           return defensive_play_personnel