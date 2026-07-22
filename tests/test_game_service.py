import os
from pathlib import Path

import pandas as pd

from game_service import game_service


class _Assignment:
    def __init__(self, primary, double):
        self.primary = primary
        self.double = double

    def assign(self):
        return self.primary, self.double


def _service(temp_data_root, output_widget):
    return game_service(str(temp_data_root), output_widget)


def test_get_game_log_and_read_game_log(temp_data_root, output_widget):
    html_path = temp_data_root / "leagues" / "SFL00004" / "lastboxlog.html"
    html_path.write_text("<html></html>", encoding="utf-8")
    service = _service(temp_data_root, output_widget)

    file_obj = service.get_game_log(str(html_path))
    try:
        assert file_obj.name.endswith("lastboxlog.html")
    finally:
        file_obj.close()

    assert service.read_game_log(str(temp_data_root)).endswith("lastboxlog.html")


def test_load_all_tables_uses_cache(monkeypatch, temp_data_root, output_widget):
    html_path = temp_data_root / "leagues" / "SFL00004" / "lastboxlog.html"
    html_path.write_text("<html><body><table><tr><td>A</td></tr></table></body></html>", encoding="utf-8")

    calls = {"count": 0}

    def fake_read_html(*_args, **_kwargs):
        calls["count"] += 1
        return [pd.DataFrame([["A"]])]

    monkeypatch.setattr("game_service.pd.read_html", fake_read_html)

    service = _service(temp_data_root, output_widget)
    first = service._load_all_tables(str(temp_data_root))
    second = service._load_all_tables(str(temp_data_root))

    assert first is second
    assert calls["count"] == 1


def test_clean_game_result_filters_and_caches(monkeypatch, temp_data_root, output_widget):
    service = _service(temp_data_root, output_widget)
    raw = pd.DataFrame(
        {
            0: [
                "A B C D Start of drive OFFENSE",  # filtered
                    "A B C PENALTY: test OFFENSE",   # filtered
                "A B C D John Smith pass completed OFFENSE",  # kept
            ]
        }
    )
    monkeypatch.setattr(service, "get_game_result", lambda *_args, **_kwargs: [raw.copy()])

    cleaned = service.get_clean_game_result(str(temp_data_root), output_widget)
    cleaned_again = service.get_clean_game_result(str(temp_data_root), output_widget)

    assert len(cleaned) == 1
    assert cleaned_again is cleaned


def test_get_game_result_delegates_to_read_html(monkeypatch, temp_data_root, output_widget):
    html_path = temp_data_root / "leagues" / "SFL00004" / "lastboxlog.html"
    html_path.write_text("<html></html>", encoding="utf-8")

    called = {"ok": False}

    def fake_read_html(_f, **_kwargs):
        called["ok"] = True
        return [pd.DataFrame([[1]])]

    monkeypatch.setattr("game_service.pd.read_html", fake_read_html)
    service = _service(temp_data_root, output_widget)
    result = service.get_game_result(str(temp_data_root), output_widget)

    assert called["ok"] is True
    assert isinstance(result, list)


def test_offense_and_defense_play_personnel_handles_index_errors(temp_data_root, output_widget):
    service = _service(temp_data_root, output_widget)
    table = pd.DataFrame([["A", "B", "C", "D", "E", "F"]])
    service._all_tables = [table, table]

    off = service.get_offensive_play_personnel(0, str(temp_data_root))
    deff = service.get_defensive_play_personnel(0, str(temp_data_root))
    assert list(off.columns) == [0, 1, 2]
    assert list(deff.columns) == [3, 4, 5]

    assert service.get_offensive_play_personnel(99, str(temp_data_root)) is None
    assert service.get_defensive_play_personnel(99, str(temp_data_root)) is None


def test_player_name_from_play_variants(temp_data_root, output_widget):
    service = _service(temp_data_root, output_widget)

    assert service.get_player_name_from_play("A B C John Smith pass completed") == "John Smith"
    assert service.get_player_name_from_play("A B C D John Smith") == "D John"
    assert service.get_player_name_from_play("too short") == ""


def test_get_play_result_with_cleanup_and_missing_index(temp_data_root, output_widget):
    service = _service(temp_data_root, output_widget)
    service.cleaned_game_log = pd.DataFrame({0: ["X Play-Action. A B C OFFENSE"]})

    assert service.get_play_result(0, str(temp_data_root), output_widget) == "X A B C "
    assert service.get_play_result(99, str(temp_data_root), output_widget) is None


def test_get_player_performance_offense_branch(monkeypatch, temp_data_root, output_widget):
    service = _service(temp_data_root, output_widget)

    monkeypatch.setattr(service, "get_play_result", lambda *_args, **_kwargs: "A B C D QB pass completed to John Smith 15")
    monkeypatch.setattr(service.ts, "check_if_in_roster", lambda *_args, **_kwargs: True)

    offense_df = pd.DataFrame(
        [
            ["FORMATION", "131", ""],
            ["X(SE) John Smith", "Primary, 2 Slant (5-8)", ""],
        ]
    )
    monkeypatch.setattr(service, "get_offensive_play_personnel", lambda *_args, **_kwargs: offense_df.copy())
    monkeypatch.setattr(service, "get_receivers_from_play", lambda *_args, **_kwargs: [["ok"]])

    result = service.get_player_performance_from_play(0, "Cleveland", str(temp_data_root), output_widget)
    assert result is not None
    assert result.shape[0] == 1


def test_get_player_performance_defense_branch(monkeypatch, temp_data_root, output_widget):
    service = _service(temp_data_root, output_widget)

    play = "A B C D QB pass fell incomplete to John Smith,"
    monkeypatch.setattr(service, "get_play_result", lambda *_args, **_kwargs: play)
    monkeypatch.setattr(service.ts, "check_if_in_roster", lambda *_args, **_kwargs: False)

    defense_df = pd.DataFrame(
        [
            ["FORMATION", "Man to Man", ""],
            ["LCB John Doe", "Rush Passer", "90"],
        ]
    )
    monkeypatch.setattr(service, "get_defensive_play_personnel", lambda *_args, **_kwargs: defense_df.copy())
    monkeypatch.setattr(service, "get_offensive_play_personnel", lambda *_args, **_kwargs: pd.DataFrame([["FORMATION", "131", ""]]))

    calls = {"rush": 0, "pass_def": 0}

    monkeypatch.setattr(service, "write_pass_rush_success_rate", lambda *_args, **_kwargs: calls.__setitem__("rush", calls["rush"] + 1))
    monkeypatch.setattr(service, "get_pass_defenders_from_play", lambda *_args, **_kwargs: calls.__setitem__("pass_def", calls["pass_def"] + 1) or [])

    result = service.get_player_performance_from_play(0, "Cleveland", str(temp_data_root), output_widget)
    assert result is not None
    assert calls["rush"] == 1
    assert calls["pass_def"] == 1


def test_get_player_performance_defense_branch_skips_accepted_penalty(monkeypatch, temp_data_root, output_widget):
    service = _service(temp_data_root, output_widget)

    play = "A B C D QB pass fell incomplete to John Smith, PENALTY on defense"
    monkeypatch.setattr(service, "get_play_result", lambda *_args, **_kwargs: play)
    monkeypatch.setattr(service.ts, "check_if_in_roster", lambda *_args, **_kwargs: False)

    defense_df = pd.DataFrame(
        [
            ["FORMATION", "Man to Man", ""],
            ["LCB John Doe", "Rush Passer", "90"],
        ]
    )
    monkeypatch.setattr(service, "get_defensive_play_personnel", lambda *_args, **_kwargs: defense_df.copy())
    monkeypatch.setattr(service, "get_offensive_play_personnel", lambda *_args, **_kwargs: pd.DataFrame([["FORMATION", "131", ""]]))

    calls = {"rush": 0}
    monkeypatch.setattr(service, "write_pass_rush_success_rate", lambda *_args, **_kwargs: calls.__setitem__("rush", calls["rush"] + 1))
    monkeypatch.setattr(service, "get_pass_defenders_from_play", lambda *_args, **_kwargs: [])

    service.get_player_performance_from_play(0, "Cleveland", str(temp_data_root), output_widget)
    assert calls["rush"] == 0


def test_get_player_performance_defense_branch_includes_declined_penalty(monkeypatch, temp_data_root, output_widget):
    service = _service(temp_data_root, output_widget)

    play = "A B C D QB pass fell incomplete to John Smith, PENALTY declined"
    monkeypatch.setattr(service, "get_play_result", lambda *_args, **_kwargs: play)
    monkeypatch.setattr(service.ts, "check_if_in_roster", lambda *_args, **_kwargs: False)

    defense_df = pd.DataFrame(
        [
            ["FORMATION", "Man to Man", ""],
            ["LCB John Doe", "Rush Passer", "90"],
        ]
    )
    monkeypatch.setattr(service, "get_defensive_play_personnel", lambda *_args, **_kwargs: defense_df.copy())
    monkeypatch.setattr(service, "get_offensive_play_personnel", lambda *_args, **_kwargs: pd.DataFrame([["FORMATION", "131", ""]]))

    calls = {"rush": 0}
    monkeypatch.setattr(service, "write_pass_rush_success_rate", lambda *_args, **_kwargs: calls.__setitem__("rush", calls["rush"] + 1))
    monkeypatch.setattr(service, "get_pass_defenders_from_play", lambda *_args, **_kwargs: [])

    service.get_player_performance_from_play(0, "Cleveland", str(temp_data_root), output_widget)
    assert calls["rush"] == 1


def test_get_player_performance_missing_play(monkeypatch, temp_data_root, output_widget):
    service = _service(temp_data_root, output_widget)
    monkeypatch.setattr(service, "get_play_result", lambda *_args, **_kwargs: None)

    assert service.get_player_performance_from_play(0, "Cleveland", str(temp_data_root), output_widget) is None


def test_get_receivers_from_play_and_pivot(in_temp_cwd, temp_data_root, output_widget):
    service = _service(temp_data_root, output_widget)

    offense = pd.DataFrame(
        [
            ["FORMATION", "131", ""],
            ["X(SE) John Smith", "Primary, 2 Slant (5-8)", ""],
            ["Z(FL) Mark Jones", "Secondary, 1 Out (5-8)", ""],
        ]
    )
    play = "A B C D QB pass completed to Alpha Beta Smith for 15 yards"

    rows = service.get_receivers_from_play(play, offense, output_widget)

    assert rows
    assert Path("receivers_in_game.csv").exists()


def test_write_receiver_pivot_summary_missing_and_empty(in_temp_cwd, temp_data_root, output_widget):
    service = _service(temp_data_root, output_widget)

    service.write_receiver_pivot_summary("does_not_exist.csv", output_widget)
    assert any("Cannot create pivot summary" in msg for msg in output_widget.messages)

    pd.DataFrame(columns=["Player Name", "Yards", "Caught?", "Route"]).to_csv("empty.csv", index=False)
    service.write_receiver_pivot_summary("empty.csv", output_widget)
    assert any("Receiver CSV is empty" in msg for msg in output_widget.messages)


def test_get_coverage_assignment_dispatch(temp_data_root, output_widget):
    service = _service(temp_data_root, output_widget)

    assert service.get_coverage_assignment("r", "p", "o", "Man to Man") is not None
    assert service.get_coverage_assignment("r", "p", "o", "Tampa-2") is not None
    assert service.get_coverage_assignment("r", "p", "o", "Cover-1") is not None
    assert service.get_coverage_assignment("r", "p", "o", "Cover-2") is not None
    assert service.get_coverage_assignment("r", "p", "o", "Cover-3 Sky") is not None
    assert service.get_coverage_assignment("r", "p", "o", "Cover-3 Cloud") is not None
    assert service.get_coverage_assignment("r", "p", "o", "Cover-4") is not None
    assert service.get_coverage_assignment("r", "p", "o", "Press-1") is not None
    assert service.get_coverage_assignment("r", "p", "o", "Press-2") is not None
    assert service.get_coverage_assignment("r", "p", "o", "Unknown") is None


def test_normalize_defensive_personnel(temp_data_root, output_widget):
    service = _service(temp_data_root, output_widget)
    df = pd.DataFrame([["LCB John Doe", "Man", "88"]])

    norm = service.normalize_defensive_play_personnel(df)
    assert list(norm.columns) == ["Position", "Player", "Assignment", "Rating"]
    assert norm.iloc[0]["Position"] == "LCB"


def test_write_pass_rush_success_rate(in_temp_cwd, temp_data_root, output_widget):
    service = _service(temp_data_root, output_widget)

    defenders = pd.DataFrame(
        [
            {"Position": "LCB", "Player": "John Doe", "Assignment": "Rush Passer", "Rating": 80},
            {"Position": "SS", "Player": "Jim Beam", "Assignment": "Blitz Passer", "Rating": 79},
            {"Position": "FS", "Player": "Safe Guy", "Assignment": "Zone", "Rating": 77},
        ]
    )
    service.write_pass_rush_success_rate(defenders, "Man to Man", "131", "QB sacked", output_widget)
    assert Path("pass_rush_success_rate.csv").exists()
    assert Path("defensive_pass_rush_pivot_summary.csv").exists()
    written = pd.read_csv("pass_rush_success_rate.csv")
    assert "Offensive Formation" in written.columns
    assert str(written.iloc[0]["Offensive Formation"]) == "131"


def test_write_pass_rush_success_rate_skips_accepted_penalty(in_temp_cwd, temp_data_root, output_widget):
    service = _service(temp_data_root, output_widget)

    defenders = pd.DataFrame(
        [
            {"Position": "LCB", "Player": "John Doe", "Assignment": "Rush Passer", "Rating": 80},
            {"Position": "SS", "Player": "Jim Beam", "Assignment": "Blitz Passer", "Rating": 79},
        ]
    )
    service.write_pass_rush_success_rate(
        defenders,
        "Man to Man",
        "131",
        "QB pass completed to Alpha Beta Smith, PENALTY on defense",
        output_widget,
        play_index=5,
    )

    assert not Path("pass_rush_success_rate.csv").exists()


def test_write_pass_rush_success_rate_includes_declined_penalty(in_temp_cwd, temp_data_root, output_widget):
    service = _service(temp_data_root, output_widget)

    defenders = pd.DataFrame(
        [
            {"Position": "LCB", "Player": "John Doe", "Assignment": "Rush Passer", "Rating": 80},
            {"Position": "SS", "Player": "Jim Beam", "Assignment": "Blitz Passer", "Rating": 79},
        ]
    )
    service.write_pass_rush_success_rate(
        defenders,
        "Man to Man",
        "131",
        "QB pass completed to Alpha Beta Smith, PENALTY declined",
        output_widget,
        play_index=5,
    )

    assert Path("pass_rush_success_rate.csv").exists()


def test_write_defensive_pivot_summary_missing_and_empty(in_temp_cwd, temp_data_root, output_widget):
    service = _service(temp_data_root, output_widget)

    service.write_defensive_pivot_summary("does_not_exist.csv", output_widget)
    assert any("Cannot create defensive pivot summary" in msg for msg in output_widget.messages)

    pd.DataFrame(
        columns=[
            "Play Index",
            "Defender Name",
            "Defender Position",
            "Defense Coverage",
            "Formation/Coverage",
            "Offensive Formation",
            "Blitz",
            "Blitz Occurred",
            "Pass Rush Success",
        ]
    ).to_csv("empty_pass_rush.csv", index=False)
    service.write_defensive_pivot_summary("empty_pass_rush.csv", output_widget)
    assert any("Pass rush CSV is empty" in msg for msg in output_widget.messages)


def test_write_defensive_pivot_summary_creates_three_tables(in_temp_cwd, temp_data_root, output_widget):
    service = _service(temp_data_root, output_widget)

    pd.DataFrame(
        [
            {
                "Play Index": 10,
                "Defender Name": "John Doe",
                "Defender Position": "LCB",
                "Defense Coverage": "Rush Passer",
                "Formation/Coverage": "Man to Man",
                "Offensive Formation": "131",
                "Blitz": 0,
                "Blitz Occurred": 1,
                "Pass Rush Success": 1,
            },
            {
                "Play Index": 10,
                "Defender Name": "Jim Beam",
                "Defender Position": "SS",
                "Defense Coverage": "Blitz Passer",
                "Formation/Coverage": "Man to Man",
                "Offensive Formation": "131",
                "Blitz": 1,
                "Blitz Occurred": 1,
                "Pass Rush Success": 0,
            },
            {
                "Play Index": 11,
                "Defender Name": "Carl Edge",
                "Defender Position": "DE",
                "Defense Coverage": "Rush Passer",
                "Formation/Coverage": "Cover-2",
                "Offensive Formation": "112",
                "Blitz": 0,
                "Blitz Occurred": 0,
                "Pass Rush Success": 1,
            },
            {
                "Play Index": 10,
                "Defender Name": "John Doe",
                "Defender Position": "LCB",
                "Defense Coverage": "Rush Passer",
                "Formation/Coverage": "Man to Man",
                "Offensive Formation": "131",
                "Blitz": 0,
                "Blitz Occurred": 1,
                "Pass Rush Success": 0,
            },
        ]
    ).to_csv("pass_rush_success_rate.csv", index=False)

    service.write_defensive_pivot_summary("pass_rush_success_rate.csv", output_widget)

    assert Path("defensive_pass_rush_pivot_summary.csv").exists()
    summary_text = Path("defensive_pass_rush_pivot_summary.csv").read_text(encoding="utf-8")
    assert "Pivot Table - Pass Rush Success Rate Per Coverage" in summary_text
    assert "Pivot Table - Pass Rush Success Rate Per Play With Blitz" in summary_text
    assert "Pivot Table - Player Pass Rush Success Rate Per Rush" in summary_text
    assert "Man to Man,1,1,1.0" in summary_text
    assert "Man to Man,1,2,0.5" not in summary_text
    assert "Yes,1,1,1.0" in summary_text
    assert "Yes,1,2,0.5" not in summary_text
    assert "John Doe,1,1,1.0" in summary_text
    assert "John Doe,1,2,0.5" not in summary_text


def test_write_pass_rush_success_rate_no_rows(in_temp_cwd, temp_data_root, output_widget):
    service = _service(temp_data_root, output_widget)
    defenders = pd.DataFrame(
        [{"Position": "FS", "Player": "Safe Guy", "Assignment": "Zone", "Rating": 77}]
    )
    service.write_pass_rush_success_rate(defenders, "Cover-2", "Shotgun", "QB pass completed", output_widget)
    assert not Path("pass_rush_success_rate.csv").exists()


def test_get_pass_defenders_from_play(in_temp_cwd, monkeypatch, temp_data_root, output_widget):
    service = _service(temp_data_root, output_widget)

    monkeypatch.setattr(service, "get_coverage_assignment", lambda *_args, **_kwargs: _Assignment("LCB", "SS"))

    offense = pd.DataFrame(
        [
            ["FORMATION", "131", ""],
            ["X(SE) John Smith", "Primary, 2 Slant (5-8)", ""],
        ]
    )
    defense = pd.DataFrame(
        [
            ["LCB John Doe", "Man to Man", "90"],
            ["SS Jim Beam", "Double X(SE)", "85"],
        ]
    )
    play = "A B C D QB pass completed to Alpha Beta Smith for 15 yards"

    result = service.get_pass_defenders_from_play("Man to Man", play, defense, output_widget, offense)

    assert result
    assert Path("pass_def_in_game.csv").exists()
