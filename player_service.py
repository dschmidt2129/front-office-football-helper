import pandas as pd

class player_service:

    def __init__(self, path):
        # cache the dataframes once instead of re‑reading every time
        self.path = path
        self._player_info = None
        self._player_record = None

    def _load_player_info(self, path=None):
        if path is None:
            path = self.path
        if self._player_info is None:
            self._player_info = pd.read_csv(path + "/leaguedata/SFL00004/player_information.csv", dtype=str)
        return self._player_info

    def _load_player_record(self, path=None):
        if path is None:
            path = self.path
        if self._player_record is None:
            self._player_record = pd.read_csv(path + "/leaguedata/SFL00004/player_record.csv", dtype=str)
        return self._player_record

    def get_player_id(self, player_name, path=None, team_id=None, team_name=None):
        """
        Return a matching Player_ID. If team_id (or team_name) supplied,
        narrow candidates to that team. Returns None when no match.
        """
        if path is None:
            path = self.path
        first, last = (player_name.split(' ', 1) + [""])[:2]
        info = self._load_player_info(path)
        candidates = info[(info.First_Name == first) & (info.Last_Name == last)]
        if candidates.empty:
            return None

        # prefer explicit team_id if provided
        record = self._load_player_record(path)
        if team_id is not None:
            rec = record[record.Player_ID.isin(candidates.Player_ID) & (record.Team == str(team_id))]
            if not rec.empty:
                return rec.Player_ID.iloc[0]
            else:
                return None

        # caller may pass team_name but resolving that to id is team_service's job;
        # if team_name provided, caller (team_service) should pass team_id instead.

        # fall back to first candidate
        if isinstance(candidates.Player_ID, pd.Series):
            return candidates.Player_ID.iloc[0]
        return candidates.Player_ID

    def get_player_team_id(self, player_id, path=None):
        if path is None:
            path = self.path
        record = self._load_player_record(path)
        matches = record[record.Player_ID == str(player_id)]
        if matches.empty:
            return None
        # If multiple records, return the first Team_ID found
        return matches.Team.iloc[0]