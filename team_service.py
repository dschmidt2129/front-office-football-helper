import pandas as pd
from player_service import player_service as ps
class team_service:

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
            
    def check_if_in_roster(self, player):   
        #  function to check if the player is on the team
        return