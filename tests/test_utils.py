import json

import pandas as pd

from src import utils


def test_load_transactions(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    expected = pd.DataFrame(
        {
            "Дата операции": ["01.12.2021", "02.12.2021"],
            "Сумма платежа": [-100.0, -200.0],
        }
    )
    expected.to_excel(data_dir / "operations.xlsx", index=False)

    monkeypatch.setattr(utils, "PATH", tmp_path)

    result = utils.load_transactions()

    pd.testing.assert_frame_equal(
        result,
        expected,
        check_dtype=False,
    )


def test_load_user_settings(tmp_path, monkeypatch):
    expected = {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL"],
    }

    settings_path = tmp_path / "user_settings.json"
    settings_path.write_text(
        json.dumps(expected, ensure_ascii=False),
        encoding="utf-8",
    )

    monkeypatch.setattr(utils, "PATH", tmp_path)

    result = utils.load_user_settings()

    assert result == expected
