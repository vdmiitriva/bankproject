import logging
import math
import os
import time
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv

from src.utils import load_user_settings

logger = logging.getLogger(__name__)
load_dotenv()


def get_greeting(date_time: str) -> str:
    curr_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    hour = curr_time.hour

    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def filter_transactions_by_date(
    transactions: pd.DataFrame, date_time: str
) -> pd.DataFrame:
    date_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    first_day = datetime(date_time.year, date_time.month, 1).date()
    end_date = date_time.date()

    operations_dates = pd.to_datetime(
        transactions["Дата операции"], dayfirst=True
    ).dt.date

    mask = (operations_dates >= first_day) & (operations_dates <= end_date)
    return transactions.loc[mask]


def get_cards_summary(transactions: pd.DataFrame) -> list[dict]:
    mask = (
        (transactions["Статус"] == "OK")
        & (transactions["Сумма платежа"] < 0)
        & (transactions["Валюта платежа"] == "RUB")
        & transactions["Номер карты"].notna()
    )

    expenses = transactions.loc[mask]
    card_totals = -expenses.groupby("Номер карты")["Сумма платежа"].sum()

    cards = []

    for card, total in card_totals.items():
        total_spent = round(float(total), 2)
        cashback = round(total_spent / 100, 2)

        cards.append(
            {
                "last_digits": str(card)[-4:],
                "total_spent": total_spent,
                "cashback": cashback,
            }
        )

    return cards


def get_top_transactions(transactions: pd.DataFrame) -> list[dict]:
    tops = transactions.sort_values(
        by="Сумма платежа",
        ascending=False,
    ).head(5)

    result = []

    for _, row in tops.iterrows():
        result.append(
            {
                "date": pd.to_datetime(row["Дата операции"], dayfirst=True).strftime(
                    "%d.%m.%Y"
                ),
                "amount": float(row["Сумма платежа"]),
                "category": row["Категория"],
                "description": row["Описание"],
            }
        )

    return result


def get_currency_rates() -> list[dict]:
    url = "https://www.cbr-xml-daily.ru/daily_json.js"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        user_currencies = load_user_settings()["user_currencies"]
        rates = []

        for cur in user_currencies:
            currency = data["Valute"][cur]
            nominal = float(currency["Nominal"])
            value = float(currency["Value"])

            if nominal <= 0 or not math.isfinite(nominal):
                raise RuntimeError(f"Некорректный номинал валюты {cur}")

            rate = value / nominal

            if rate <= 0 or not math.isfinite(rate):
                raise RuntimeError(f"Некорректный курс валюты {cur}")

            rates.append(
                {
                    "currency": str(cur),
                    "rate": float(rate),
                }
            )

        return rates

    except requests.exceptions.RequestException as error:
        raise RuntimeError("Не удалось получить курсы валют") from error

    except (ValueError, TypeError, KeyError, ZeroDivisionError) as error:
        raise RuntimeError("Не удалось обработать данные о курсах валют") from error


def get_stock_prices() -> list[dict]:
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")

    if not api_key:
        raise RuntimeError("Не найден API-ключ Alpha Vantage")

    url = "https://www.alphavantage.co/query"
    user_stocks = load_user_settings()["user_stocks"]
    stocks = []

    for index, stock in enumerate(user_stocks):
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": stock,
            "apikey": api_key,
        }

        try:
            response = requests.get(
                url,
                params=params,
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()

        except requests.exceptions.RequestException as error:
            raise RuntimeError(f"Не удалось получить цену акции {stock}") from error

        except ValueError as error:
            raise RuntimeError(f"Некорректный ответ API для акции {stock}") from error

        if not isinstance(data, dict):
            raise RuntimeError(f"Некорректный формат ответа API для акции {stock}")

        if "Note" in data or "Information" in data:
            raise RuntimeError("Alpha Vantage ограничил количество запросов")

        if "Error Message" in data:
            raise RuntimeError(f"Alpha Vantage не смог найти акцию {stock}")

        quote = data.get("Global Quote")

        if not quote or "05. price" not in quote:
            raise RuntimeError(f"Не удалось получить цену акции {stock}")

        try:
            price = float(quote["05. price"])
        except (ValueError, TypeError) as error:
            raise RuntimeError(f"Некорректная цена акции {stock}") from error

        if price <= 0 or not math.isfinite(price):
            raise RuntimeError(f"Цена акции {stock} должна быть больше нуля")

        stocks.append(
            {
                "stock": str(stock),
                "price": float(price),
            }
        )

        if index < len(user_stocks) - 1:
            time.sleep(1.2)

    return stocks


def get_main_page(date_time: str, transactions: pd.DataFrame) -> dict:
    filt_transactions = filter_transactions_by_date(transactions, date_time)

    try:
        currency_rates = get_currency_rates()
    except RuntimeError:
        logger.exception("Не удалось получить курсы валют")
        currency_rates = []

    try:
        stock_prices = get_stock_prices()
    except RuntimeError:
        logger.exception("Не удалось получить цены акций")
        stock_prices = []

    return {
        "greeting": get_greeting(date_time),
        "cards": get_cards_summary(filt_transactions),
        "top_transactions": get_top_transactions(filt_transactions),
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }
