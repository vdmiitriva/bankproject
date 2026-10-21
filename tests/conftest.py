from unittest.mock import patch

import pandas as pd
import pytest


@pytest.fixture
def search_transactions():
    transactions = pd.DataFrame(
        {
            "Описание": ["Магнит", "Пятёрочка", "Поезд"],
            "Категория": ["Супермаркеты", "Продукты", "Поезд"],
        }
    )

    return transactions


@pytest.fixture
def report_transactions():
    return pd.DataFrame(
        {
            "Дата операции": [
                "31.12.2021",
                "31.12.2021",
                "31.12.2021",
                "31.12.2021",
            ],
            "Статус": [
                "OK",
                "FAILED",
                "OK",
                "OK",
            ],
            "Валюта платежа": [
                "RUB",
                "RUB",
                "USD",
                "RUB",
            ],
            "Сумма платежа": [
                -1000,
                -2000,
                -3000,
                500,
            ],
        }
    )


@pytest.fixture
def view_transactions():
    """Шесть тестовых банковских операций."""
    return pd.DataFrame(
        {
            "Дата операции": ["01.12.2021"] * 6,
            "Дата платежа": ["01.12.2021"] * 6,
            "Номер карты": ["*4556"] * 6,
            "Статус": ["OK"] * 6,
            "Сумма операции": [
                -100.0,
                -200.0,
                -300.0,
                -400.0,
                -500.0,
                -600.0,
            ],
            "Валюта операции": ["RUB"] * 6,
            "Сумма платежа": [
                -100.0,
                -200.0,
                -300.0,
                -400.0,
                -500.0,
                -600.0,
            ],
            "Валюта платежа": ["RUB"] * 6,
            "Кэшбэк": [1.0] * 6,
            "Категория": ["Супермаркеты"] * 6,
            "MCC": [5411] * 6,
            "Описание": [
                "Операция 1",
                "Операция 2",
                "Операция 3",
                "Операция 4",
                "Операция 5",
                "Операция 6",
            ],
            "Бонусы (включая кешбэк)": [1.0] * 6,
            "Округление на инвесткопилку": [0.0] * 6,
            "Сумма операции с округлением": [
                -100.0,
                -200.0,
                -300.0,
                -400.0,
                -500.0,
                -600.0,
            ],
        }
    )


@pytest.fixture
def mocked_external_apis():
    """Подменяет обращения к API валют и акций."""
    with (
        patch(
            "src.views.get_currency_rates",
            return_value=[
                {"currency": "USD", "rate": 90.0},
                {"currency": "EUR", "rate": 100.0},
            ],
        ) as mock_currency_rates,
        patch(
            "src.views.get_stock_prices",
            return_value=[
                {"stock": "AAPL", "price": 200.0},
            ],
        ) as mock_stock_prices,
    ):
        yield {
            "currency_rates": mock_currency_rates,
            "stock_prices": mock_stock_prices,
        }
