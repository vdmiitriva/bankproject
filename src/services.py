import json

import pandas as pd


def simple_search(transactions: pd.DataFrame, query: str) -> list[dict]:
    description_mask = transactions["Описание"].str.contains(
        query, case=False, na=False, regex=False
    )
    category_mask = transactions["Категория"].str.contains(
        query, case=False, na=False, regex=False
    )

    filtered_transactions = transactions[description_mask | category_mask]

    json_data = filtered_transactions.to_json(
        orient="records",
        force_ascii=False,
        date_format="iso",
    )

    return json.loads(json_data)
