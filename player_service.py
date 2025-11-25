import pandas as pd

class player_service:
    
    def __init__(self, path):
        # no variables initialized
        pass

    def get_player_id(self, player_name, path):
        # returns the player id
        print('Getting player info for : ' + player_name)
        player_info = pd.read_csv(path + "/leaguedata/SFL00004/player_information.csv")
        player_first_name = player_name.split(' ')[0]
        player_last_name = player_name.split(' ')[1]
        player_info.set_index(['First_Name', 'Last_Name'], inplace=True)
        player_info.sort_index(inplace=True) # was receiving  PerformanceWarning: indexing past lexsort depth may impact performance. this indicates that the index is not sorted.
        player_id_series = player_info.loc[(player_first_name, player_last_name), player_info.columns[0]]
        if isinstance(player_id_series, pd.Series):
            # Multiple players with the same name, return the first one.
            player_id = player_id_series.iloc[0]
        else:
            player_id = player_id_series # It's already a scalar
        if player_id is None:
            return
        # print('player id: ' + str(player_id))
        return player_id

    def get_player_team_id(self, player_id, path):
        # returns the player's team id
        player_record = pd.read_csv(path + "/leaguedata/SFL00004/player_record.csv")
        player_record.set_index('Player_ID', inplace=True)
        player_record.sort_index(inplace=True) # was receiving  PerformanceWarning: indexing past lexsort depth may impact performance. this indicates that the index is not sorted.
        player_team_id_series = player_record.loc[player_id, player_record.columns[4]]
        if isinstance(player_team_id_series, pd.Series):
            player_team_id = player_team_id_series.iloc[0]
        else:
            player_team_id = player_team_id_series
        if player_team_id is None:
            return
        # print('player team id: ' + str(player_team_id))
        return player_team_id