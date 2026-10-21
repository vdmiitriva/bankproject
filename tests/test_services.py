from src.services import simple_search


def test_simple_search_description(search_transactions):
    result = simple_search(search_transactions, "магнит")

    assert len(result) == 1
    assert result[0]["Описание"] == "Магнит"


def test_simple_search_category(search_transactions):
    result = simple_search(search_transactions, "продукты")

    assert len(result) == 1
    assert result[0]["Категория"] == "Продукты"


def test_simple_search_blank(search_transactions):
    result = simple_search(search_transactions, "кинотеатр")

    assert len(result) == 0


def test_simple_search_both(search_transactions):
    result = simple_search(search_transactions, "поезд")

    assert len(result) == 1
    assert [item["Описание"] for item in result] == ["Поезд"]


def test_simple_search_case_insensitive(search_transactions):
    result = simple_search(search_transactions, "МАГНИТ")

    assert len(result) == 1
    assert result[0]["Описание"] == "Магнит"


def test_simple_search_returns_multiple_matches(search_transactions):
    transactions = search_transactions.copy()
    transactions.loc[3] = ["Магнит у дома", "Продукты"]
    transactions.loc[4] = ["Покупка продуктов", "Магазины"]

    result = simple_search(transactions, "маг")

    assert len(result) == 3
    assert [item["Описание"] for item in result] == [
        "Магнит",
        "Магнит у дома",
        "Покупка продуктов",
    ]


def test_simple_search_handles_missing_values():
    import pandas as pd

    transactions = pd.DataFrame(
        {
            "Описание": ["Магнит", None, "Поезд"],
            "Категория": [None, "Продукты", "Транспорт"],
        }
    )

    result = simple_search(transactions, "продукты")

    assert len(result) == 1
    assert result[0]["Категория"] == "Продукты"


def test_simple_search_does_not_modify_original(search_transactions):
    import pandas as pd

    original = search_transactions.copy(deep=True)

    simple_search(search_transactions, "магнит")

    pd.testing.assert_frame_equal(search_transactions, original)
