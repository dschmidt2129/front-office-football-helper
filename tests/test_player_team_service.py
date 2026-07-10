import pandas as pd

from player_service import player_service
from team_service import team_service


def _write_roster_csvs(base):
    leaguedata = base / "leaguedata" / "SFL00004"
    pd.DataFrame(
        [
            {"First_Name": "John", "Last_Name": "Doe", "Player_ID": "1"},
            {"First_Name": "John", "Last_Name": "Doe", "Player_ID": "2"},
            {"First_Name": "Jane", "Last_Name": "Smith", "Player_ID": "3"},
        ]
    ).to_csv(leaguedata / "player_information.csv", index=False)
    pd.DataFrame(
        [
            {"Player_ID": "1", "Team": "30"},
            {"Player_ID": "2", "Team": "21"},
            {"Player_ID": "3", "Team": "14"},
        ]
    ).to_csv(leaguedata / "player_record.csv", index=False)
    pd.DataFrame(
        [
            {"Home_City": "Cleveland", "Team": 30},
            {"Home_City": "Philadelphia", "Team": 21},
            {"Home_City": "Miami", "Team": 14},
        ]
    ).to_csv(leaguedata / "team_information.csv", index=False)


def test_player_service_loaders_and_cache(temp_data_root):
    _write_roster_csvs(temp_data_root)
    service = player_service(str(temp_data_root))

    info_1 = service._load_player_info()
    info_2 = service._load_player_info()
    record_1 = service._load_player_record()
    record_2 = service._load_player_record()

    assert info_1 is info_2
    assert record_1 is record_2


def test_player_service_get_player_id_variants(temp_data_root):
    _write_roster_csvs(temp_data_root)
    service = player_service(str(temp_data_root))

    assert service.get_player_id("No Name") is None
    assert service.get_player_id("John Doe", team_id=30) == "1"
    assert service.get_player_id("John Doe", team_id=999) is None
    assert service.get_player_id("John Doe") == "1"


def test_player_service_get_player_team_id(temp_data_root):
    _write_roster_csvs(temp_data_root)
    service = player_service(str(temp_data_root))

    assert service.get_player_team_id("1") == "30"
    assert service.get_player_team_id("999") is None


def test_team_service_loaders_and_id_lookup(temp_data_root):
    _write_roster_csvs(temp_data_root)
    service = team_service(str(temp_data_root))

    team_info = service._load_team_info(str(temp_data_root))
    assert not team_info.empty
    assert service._load_team_info(str(temp_data_root)) is team_info

    player_info = service._load_player_info(str(temp_data_root))
    assert not player_info.empty
    assert service._load_player_info(str(temp_data_root)) is player_info

    player_record = service._load_player_record(str(temp_data_root))
    assert not player_record.empty
    assert service._load_player_record(str(temp_data_root)) is player_record

    assert service.get_team_id("Cleveland", str(temp_data_root)) == 30
    assert service.get_team_id("Nowhere", str(temp_data_root)) is None


def test_team_service_check_if_in_roster(temp_data_root):
    _write_roster_csvs(temp_data_root)
    service = team_service(str(temp_data_root))

    assert service.check_if_in_roster("John Doe", "Cleveland", str(temp_data_root)) is True
    assert service.check_if_in_roster("John Doe", "Philadelphia", str(temp_data_root)) is True
    assert service.check_if_in_roster("John Doe", "Miami", str(temp_data_root)) is False
    assert service.check_if_in_roster("John Doe", "Unknown", str(temp_data_root)) is False
