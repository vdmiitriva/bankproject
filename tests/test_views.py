from src.views import get_main_page


def test_get_main_page_returns_required_keys(
    view_transactions,
    mocked_external_apis,
):
    result = get_main_page(
        "2021-12-01 12:00:00",
        view_transactions,
    )

    assert set(result.keys()) == {
        "greeting",
        "cards",
        "top_transactions",
        "currency_rates",
        "stock_prices",
    }


def test_get_main_page_returns_five_transactions(
    view_transactions,
    mocked_external_apis,
):
    result = get_main_page(
        "2021-12-01 12:00:00",
        view_transactions,
    )

    assert len(result["top_transactions"]) == 5


def test_get_main_page_sorts_transactions(
    view_transactions,
    mocked_external_apis,
):
    result = get_main_page(
        "2021-12-01 12:00:00",
        view_transactions,
    )

    descriptions = [
        transaction["description"]
        for transaction in result["top_transactions"]
    ]

    assert descriptions == [
        "Операция 1",
        "Операция 2",
        "Операция 3",
        "Операция 4",
        "Операция 5",
    ]


def test_get_main_page_calculates_card_summary(
    view_transactions,
    mocked_external_apis,
):
    result = get_main_page(
        "2021-12-01 12:00:00",
        view_transactions,
    )

    assert result["cards"] == [
        {
            "last_digits": "4556",
            "total_spent": 2100.0,
            "cashback": 21,
        }
    ]


def test_get_main_page_returns_greeting(
    view_transactions,
    mocked_external_apis,
):
    result = get_main_page(
        "2021-12-01 12:00:00",
        view_transactions,
    )

    assert result["greeting"] == "Добрый день"


def test_get_main_page_uses_external_api_mocks(
    view_transactions,
    mocked_external_apis,
):
    result = get_main_page(
        "2021-12-01 12:00:00",
        view_transactions,
    )

    mocked_external_apis["currency_rates"].assert_called_once_with()
    mocked_external_apis["stock_prices"].assert_called_once_with()

    assert result["currency_rates"] == [
        {"currency": "USD", "rate": 90.0},
        {"currency": "EUR", "rate": 100.0},
    ]

    assert result["stock_prices"] == [
        {"stock": "AAPL", "price": 200.0},
    ]
