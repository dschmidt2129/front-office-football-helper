from front_office_football_service import front_office_football_service


class DummyGameService:
    def __init__(self, *_args, **_kwargs):
        self.calls = []

    def get_clean_game_result(self, *_args, **_kwargs):
        return ["play1", "play2", "play3"]

    def get_player_performance_from_play(self, index, *_args, **_kwargs):
        self.calls.append(index)
        if index == 1:
            raise IndexError("bad play")
        if index == 2:
            raise RuntimeError("unexpected")
        return {"index": index}


def test_iterate_through_gamelog_handles_success_and_exceptions(monkeypatch, output_widget):
    monkeypatch.setattr("front_office_football_service.gs", DummyGameService)

    service = front_office_football_service("path", output_widget)
    service.iterate_through_gamelog("path", None, 0, "Cleveland", output_widget)

    assert "Processing play 0" in output_widget.messages
    assert any(msg.startswith("IndexError:") for msg in output_widget.messages)
    assert any(msg.startswith("Unexpected error:") for msg in output_widget.messages)
    assert output_widget.messages[-1] == "Finished processing all plays."
