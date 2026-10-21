import pandas as pd


def simple_search(transactions: pd.DataFrame, query: str) -> pd.DataFrame:
    description_mask = transactions["Описание"].str.contains(
        query, case=False, na=False, regex=False
    )
    category_mask = transactions["Категория"].str.contains(
        query, case=False, na=False, regex=False
    )

    mask = description_mask | category_mask
    return transactions[mask]
