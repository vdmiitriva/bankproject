import json
from pathlib import Path

import pandas as pd

PATH = Path(__file__).resolve().parent.parent


def load_transactions() -> pd.DataFrame:
    transactions_path = PATH / "data" / "operations.xlsx"
    transactions = pd.read_excel(transactions_path)
    return transactions


def load_user_settings() -> dict:
    settings_path = PATH / "user_settings.json"

    with settings_path.open("r", encoding="utf-8") as file:
        user_settings = json.load(file)

    return user_settings
