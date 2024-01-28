import pandas as pd

class player_service:
    
    def __init__(self):
        # no variables initialized
        pass

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