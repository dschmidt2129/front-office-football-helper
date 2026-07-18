import pandas as pd
from player_service import player_service as ps

class team_service:
    def __init__(self, path):
        self.path = path
        self._team_info = None
        self._player_info = None
        self._player_record = None
        self._team_id_by_city = None
        self._roster_name_index = None
        # attach a player_service instance for name+team lookups
        self.ps = ps(path)

    def _load_team_info(self, path=None):
        if path is None:
            path = self.path
        if self._team_info is None:
            self._team_info = pd.read_csv(path+"/leaguedata/SFL00004/team_information.csv")
        return self._team_info

    def _load_player_info(self, path=None):
        if path is None:
            path = self.path
        if self._player_info is None:
            self._player_info = pd.read_csv(path+"/leaguedata/SFL00004/player_information.csv", dtype=str)
        return self._player_info

    def _load_player_record(self, path=None):
        if path is None:
            path = self.path
        if self._player_record is None:
            self._player_record = pd.read_csv(path+"/leaguedata/SFL00004/player_record.csv", dtype=str)
        return self._player_record

    def _normalize_player_name(self, player_name):
        return " ".join(str(player_name).strip().split()).lower()

    def _build_team_lookup(self, path=None):
        if self._team_id_by_city is not None:
            return
        team_info = self._load_team_info(path)
        self._team_id_by_city = {}
        for _, row in team_info.iterrows():
            city = str(row.get('Home_City', '')).strip()
            team_id = row.get('Team')
            if city and pd.notna(team_id):
                self._team_id_by_city[city] = int(team_id)

    def _build_roster_lookup(self, path=None):
        if self._roster_name_index is not None:
            return
        player_info = self._load_player_info(path)
        player_record = self._load_player_record(path)

        merged = player_record[['Player_ID', 'Team']].merge(
            player_info[['Player_ID', 'First_Name', 'Last_Name']],
            on='Player_ID',
            how='inner'
        )

        self._roster_name_index = {}
        for _, row in merged.iterrows():
            team_id = str(row['Team']).strip()
            full_name = f"{str(row['First_Name']).strip()} {str(row['Last_Name']).strip()}"
            normalized_name = self._normalize_player_name(full_name)
            if not team_id or not normalized_name:
                continue
            key = (team_id, normalized_name)
            self._roster_name_index[key] = row['Player_ID']

    def get_team_id(self, team, path):
        # Team ID reference:
        # Cleveland: 30, Las Vegas: 20, Miami: 14
        # Indianapolis: 11, Philadelphia: 21
        if path is None:
            path = self.path
        self._build_team_lookup(path)
        team_id = self._team_id_by_city.get(team)
        if team_id is None:
            print(f"No team found for: {team}")
            return None
        return team_id
            
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
        self._build_roster_lookup(path)
        normalized_name = self._normalize_player_name(player_name)
        if (str(team_id), normalized_name) in self._roster_name_index:
            return True
        # Fallback for any unexpected edge cases not covered by the cache key shape.
        player_id = self.ps.get_player_id(player_name, path=path, team_id=team_id)
        return player_id is not None