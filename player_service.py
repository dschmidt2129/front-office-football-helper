import pandas as pd

class player_service:
    
    def __init__(self):
        # no variables initialized
        pass

    def get_player_id(self, player_name, player_pos):
        player_info = pd.read_csv("resources/player_information.csv")
        

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