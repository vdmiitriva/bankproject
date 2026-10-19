from src.services import simple_search


def test_simple_search_description(search_transactions):
    result = simple_search(search_transactions, "магнит")

    assert len(result) == 1
    assert result.iloc[0]["Описание"] == "Магнит"

def test_simple_search_category(search_transactions):
    result = simple_search(search_transactions, "продукты")

    assert len(result) == 1
    assert result.iloc[0]["Категория"] == "Продукты"

def test_simple_search_blank(search_transactions):
    result = simple_search(search_transactions, "кинотеатр")

    assert len(result) == 0

def test_simple_search_both(search_transactions):
    result = simple_search(search_transactions, "поезд")

    assert len(result) == 1
    assert result["Описание"].tolist() == ["Поезд"]