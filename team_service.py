import pandas as pd
from player_service import player_service as ps

class team_service:
    def __init__(self, path):
        self.path = path
        self._team_info = None
        self._player_info = None
        self._player_record = None
        # attach a player_service instance for name+team lookups
        self.ps = ps(path)

    def _load_team_info(self, path):
        if self._team_info is None:
            self._team_info = pd.read_csv(path+"/leaguedata/SFL00004/team_information.csv")
        return self._team_info

    def _load_player_info(self, path):
        if self._player_info is None:
            self._player_info = pd.read_csv(path+"/leaguedata/SFL00004/player_information.csv")
        return self._player_info

    def _load_player_record(self, path):
        if self._player_record is None:
            self._player_record = pd.read_csv(path+"/leaguedata/SFL00004/player_record.csv")
        return self._player_record

    def get_team_id(self, team, path):
        # Team ID reference:
        # Cleveland: 30, Las Vegas: 20, Miami: 14
        # Indianapolis: 11, Philadelphia: 21
        team_info = self._load_team_info(path)
        matches = team_info[team_info['Home_City'] == team]
        if matches.empty:
            print(f"No team found for: {team}")
            return None
        return int(matches['Team'].iloc[0])
            
    def check_if_in_roster(self, player_name, team_name, path):
        """
        Return True only if player_name appears on the given team's roster.
        Uses player_service.get_player_id with a resolved team_id to disambiguate duplicates.
        """
        if path is None:
            path = self.path
        team_id = self.get_team_id(team_name, path)
        if team_id is None:
            return False
        player_id = self.ps.get_player_id(player_name, path=path, team_id=team_id)
        return player_id is not None