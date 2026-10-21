import pandas as pd
import pytest
import requests

from src.views import (
    filter_transactions_by_date,
    get_currency_rates,
    get_greeting,
    get_main_page,
    get_stock_prices,
)


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
        transaction["description"] for transaction in result["top_transactions"]
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


def test_get_currency_rates_returns_rates(monkeypatch):
    from src import views

    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "Valute": {
                    "USD": {"Value": 90.0, "Nominal": 1},
                    "EUR": {"Value": 100.0, "Nominal": 1},
                }
            }

    monkeypatch.setattr(
        views.requests,
        "get",
        lambda *args, **kwargs: MockResponse(),
    )
    monkeypatch.setattr(
        views,
        "load_user_settings",
        lambda: {"user_currencies": ["USD", "EUR"]},
    )

    assert get_currency_rates() == [
        {"currency": "USD", "rate": 90.0},
        {"currency": "EUR", "rate": 100.0},
    ]


def test_get_currency_rates_handles_network_error(monkeypatch):
    from src import views

    def raise_network_error(*args, **kwargs):
        raise requests.exceptions.ConnectionError("Connection failed")

    monkeypatch.setattr(
        views.requests,
        "get",
        raise_network_error,
    )

    with pytest.raises(RuntimeError, match="Не удалось получить курсы валют"):
        get_currency_rates()


def test_get_stock_prices_returns_prices(monkeypatch):
    from src import views

    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "Global Quote": {
                    "05. price": "200.0000",
                }
            }

    monkeypatch.setenv("ALPHA_VANTAGE_API_KEY", "test-api-key")
    monkeypatch.setattr(
        views,
        "load_user_settings",
        lambda: {"user_stocks": ["AAPL"]},
    )
    monkeypatch.setattr(
        views.requests,
        "get",
        lambda *args, **kwargs: MockResponse(),
    )

    monkeypatch.setattr(views.time, "sleep", lambda seconds: None)

    assert get_stock_prices() == [
        {"stock": "AAPL", "price": 200.0},
    ]


def test_get_stock_prices_handles_api_limit(monkeypatch):
    from src import views

    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "Note": "API call frequency limit reached",
            }

    monkeypatch.setenv("ALPHA_VANTAGE_API_KEY", "test-api-key")
    monkeypatch.setattr(
        views,
        "load_user_settings",
        lambda: {"user_stocks": ["AAPL"]},
    )
    monkeypatch.setattr(
        views.requests,
        "get",
        lambda *args, **kwargs: MockResponse(),
    )

    with pytest.raises(
        RuntimeError,
        match="Alpha Vantage ограничил количество запросов",
    ):
        get_stock_prices()


def test_get_stock_prices_requires_api_key(monkeypatch):
    monkeypatch.delenv("ALPHA_VANTAGE_API_KEY", raising=False)

    with pytest.raises(
        RuntimeError,
        match="Не найден API-ключ Alpha Vantage",
    ):
        get_stock_prices()


def test_get_stock_prices_handles_invalid_price(monkeypatch):
    from src import views

    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "Global Quote": {
                    "05. price": "not-a-number",
                }
            }

    monkeypatch.setenv("ALPHA_VANTAGE_API_KEY", "test-api-key")
    monkeypatch.setattr(
        views,
        "load_user_settings",
        lambda: {"user_stocks": ["AAPL"]},
    )
    monkeypatch.setattr(
        views.requests,
        "get",
        lambda *args, **kwargs: MockResponse(),
    )
    monkeypatch.setattr(views.time, "sleep", lambda seconds: None)

    with pytest.raises(
        RuntimeError,
        match="Некорректная цена акции AAPL",
    ):
        get_stock_prices()


@pytest.mark.parametrize(
    ("date_time", "expected"),
    [
        ("2021-12-01 05:59:00", "Доброй ночи"),
        ("2021-12-01 06:00:00", "Доброе утро"),
        ("2021-12-01 11:59:00", "Доброе утро"),
        ("2021-12-01 12:00:00", "Добрый день"),
        ("2021-12-01 17:59:00", "Добрый день"),
        ("2021-12-01 18:00:00", "Добрый вечер"),
        ("2021-12-01 22:59:00", "Добрый вечер"),
        ("2021-12-01 23:00:00", "Доброй ночи"),
    ],
)
def test_get_greeting_time_boundaries(date_time, expected):
    assert get_greeting(date_time) == expected


def test_filter_transactions_by_date():
    transactions = pd.DataFrame(
        {
            "Дата операции": [
                "31.10.2021",
                "01.11.2021",
                "15.11.2021",
                "30.11.2021",
                "01.12.2021",
            ],
            "Сумма платежа": [-100, -200, -300, -400, -500],
        }
    )

    result = filter_transactions_by_date(
        transactions,
        "2021-11-15 12:00:00",
    )

    assert result["Дата операции"].tolist() == [
        "01.11.2021",
        "15.11.2021",
    ]


def test_filter_transactions_by_date_does_not_modify_original():
    transactions = pd.DataFrame(
        {
            "Дата операции": ["01.11.2021", "15.11.2021", "01.12.2021"],
            "Сумма платежа": [-100, -200, -300],
        }
    )
    original = transactions.copy(deep=True)

    filter_transactions_by_date(
        transactions,
        "2021-11-15 12:00:00",
    )

    pd.testing.assert_frame_equal(transactions, original)


def test_get_main_page_with_empty_transactions(mocked_external_apis):
    empty_transactions = pd.DataFrame(
        columns=[
            "Дата операции",
            "Дата платежа",
            "Номер карты",
            "Статус",
            "Сумма операции",
            "Валюта операции",
            "Сумма платежа",
            "Валюта платежа",
            "Кэшбэк",
            "Категория",
            "MCC",
            "Описание",
            "Бонусы (включая кешбэк)",
            "Округление на инвесткопилку",
            "Сумма операции с округлением",
        ]
    )

    result = get_main_page(
        "2021-12-01 12:00:00",
        empty_transactions,
    )

    assert result["greeting"] == "Добрый день"
    assert result["cards"] == []
    assert result["top_transactions"] == []
    assert result["currency_rates"] == [
        {"currency": "USD", "rate": 90.0},
        {"currency": "EUR", "rate": 100.0},
    ]
    assert result["stock_prices"] == [
        {"stock": "AAPL", "price": 200.0},
    ]


def test_get_currency_rates_handles_http_error(monkeypatch):
    from src import views

    def raise_http_error(*args, **kwargs):
        raise requests.exceptions.HTTPError("500 Server Error")

    monkeypatch.setattr(views.requests, "get", raise_http_error)

    with pytest.raises(
        RuntimeError,
        match="Не удалось получить курсы валют",
    ):
        get_currency_rates()


def test_get_stock_prices_handles_network_error(monkeypatch):
    from src import views

    monkeypatch.setenv("ALPHA_VANTAGE_API_KEY", "test-api-key")
    monkeypatch.setattr(
        views,
        "load_user_settings",
        lambda: {"user_stocks": ["AAPL"]},
    )

    def raise_network_error(*args, **kwargs):
        raise requests.exceptions.ConnectionError("Connection failed")

    monkeypatch.setattr(views.requests, "get", raise_network_error)

    with pytest.raises(
        RuntimeError,
        match="Не удалось получить цену акции AAPL",
    ):
        get_stock_prices()


def test_get_stock_prices_waits_between_requests(monkeypatch):
    from src import views

    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"Global Quote": {"05. price": "200.00"}}

    monkeypatch.setenv("ALPHA_VANTAGE_API_KEY", "test-api-key")
    monkeypatch.setattr(
        views,
        "load_user_settings",
        lambda: {"user_stocks": ["AAPL", "MSFT"]},
    )
    monkeypatch.setattr(
        views.requests,
        "get",
        lambda *args, **kwargs: MockResponse(),
    )

    calls = []
    monkeypatch.setattr(
        views.time,
        "sleep",
        lambda seconds: calls.append(seconds),
    )

    result = get_stock_prices()

    assert len(result) == 2
    assert calls == [1.2]


def test_get_main_page_handles_currency_api_error(
    view_transactions,
    monkeypatch,
):
    from src import views

    monkeypatch.setattr(
        views,
        "get_currency_rates",
        lambda: (_ for _ in ()).throw(RuntimeError("API недоступен")),
    )
    monkeypatch.setattr(
        views,
        "get_stock_prices",
        lambda: [{"stock": "AAPL", "price": 200.0}],
    )

    result = get_main_page(
        "2021-12-01 12:00:00",
        view_transactions,
    )

    assert result["currency_rates"] == []
    assert result["stock_prices"] == [{"stock": "AAPL", "price": 200.0}]
    assert result["greeting"] == "Добрый день"


def test_get_main_page_handles_stock_api_error(
    view_transactions,
    monkeypatch,
):
    from src import views

    monkeypatch.setattr(
        views,
        "get_currency_rates",
        lambda: [{"currency": "USD", "rate": 90.0}],
    )
    monkeypatch.setattr(
        views,
        "get_stock_prices",
        lambda: (_ for _ in ()).throw(RuntimeError("API недоступен")),
    )

    result = get_main_page(
        "2021-12-01 12:00:00",
        view_transactions,
    )

    assert result["currency_rates"] == [{"currency": "USD", "rate": 90.0}]
    assert result["stock_prices"] == []
    assert result["greeting"] == "Добрый день"
