from pathlib import Path

import main


def test_folder_selector_default_and_browse(monkeypatch, tmp_path):
    selector = main.FOF8FolderSelector()
    assert selector.get_selected_path()

    picked = str(tmp_path)
    monkeypatch.setattr(main.QFileDialog, "getExistingDirectory", lambda *args, **kwargs: picked)
    selector.browse_folder()
    assert selector.get_selected_path() == picked
    assert selector.path_display.text() == picked


def test_home_clear_log_and_print_selected_path(monkeypatch, capsys):
    home = main.Home()
    home.output_box.append("hello")
    home.clear_log_click()
    assert home.output_box.messages == []

    monkeypatch.setattr(home.folder_selector, "get_selected_path", lambda: "C:/fake")
    home.print_selected_path()
    out = capsys.readouterr().out
    assert "C:/fake" in out


def test_process_game_click_invalid_and_valid(monkeypatch, tmp_path):
    home = main.Home()

    invalid = str(tmp_path / "missing")
    monkeypatch.setattr(home.folder_selector, "get_selected_path", lambda: invalid)
    home.process_game_click()
    assert "Invalid path selected" in home.output_box.messages[0]

    valid = str(tmp_path)
    monkeypatch.setattr(home.folder_selector, "get_selected_path", lambda: valid)

    class DummyFOF:
        def __init__(self, *_args, **_kwargs):
            self.called = False

        def iterate_through_gamelog(self, *_args, **_kwargs):
            self.called = True

    class DummyGameService:
        def __init__(self, *_args, **_kwargs):
            return None

    monkeypatch.setitem(__import__("sys").modules, "front_office_football_service", type("mod", (), {"front_office_football_service": DummyFOF}))
    monkeypatch.setitem(__import__("sys").modules, "game_service", type("mod", (), {"game_service": DummyGameService}))

    home.process_game_click()
