from datetime import datetime
import pandas as pd
import requests
from src.utils import load_user_settings
import os
from dotenv import load_dotenv
load_dotenv()
import time

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

def filter_transactions_by_date(transactions: pd.DataFrame, date_time: str) -> pd.DataFrame:
    date_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    first_day = datetime(date_time.year, date_time.month, 1).date()
    end_date = date_time.date()
    operations_dates = pd.to_datetime(transactions["Дата операции"], dayfirst=True).dt.date
    mask = (operations_dates >= first_day) & (operations_dates <= end_date)
    return transactions[mask]

def get_cards_summary(transactions: pd.DataFrame) -> list[dict]:
    mask = (
            (transactions.iloc[:, 3] == "OK")
            & (transactions.iloc[:, 6] < 0)
            & (transactions.iloc[:, 7] == "RUB")
            & (transactions.iloc[:, 2].notna())
    )
    expenses = transactions[mask]
    card_totals = -expenses.groupby(expenses.iloc[:, 2])[expenses.columns[6]].sum()

    cards = []

    for card, total in card_totals.items():
        cashback = total / 100

        cards.append({
            "last_digits": card[-4:],
            "total_spent": round(float(total), 2),
            "cashback": cashback
        })

    return cards

def get_top_transactions(transactions: pd.DataFrame) -> list[dict]:
    tops = transactions.sort_values(by="Сумма платежа", ascending=False).head(5)

    result = []

    for _, row in tops.iterrows():
        r = {
            "date": pd.to_datetime(row["Дата операции"], dayfirst=True).strftime("%d.%m.%Y"),
            "amount": row["Сумма платежа"],
            "category": row["Категория"],
            "description": row["Описание"]
        }
        result.append(r)

    return result

def get_currency_rates() -> list[dict]:
    url = "https://www.cbr-xml-daily.ru/daily_json.js"

    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    user_currencies = load_user_settings()["user_currencies"]
    rates = []

    for cur in user_currencies:
        currency = data["Valute"][cur]
        rate = currency["Value"] / currency["Nominal"]

        rates.append({
            "currency": cur,
            "rate": rate
        })

    return rates


def get_stock_prices() -> list[dict]:
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        raise ValueError("Alpha Vantage API key not found")

    url = "https://www.alphavantage.co/query"
    user_stocks = load_user_settings()["user_stocks"]
    stocks = []

    for stock in user_stocks:
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": stock,
            "apikey": api_key,
        }

        response = requests.get(url, params=params, timeout=15)
        data = response.json()

        quote = data.get("Global Quote")
        if not quote:
            raise ValueError(f"Could not get price for {stock}")

        stocks.append({
            "stock": stock,
            "price": float(quote["05. price"]),
        })

        time.sleep(1.2)

    return stocks


def get_main_page(date_time: str, transactions: pd.DataFrame) -> dict:
    filt_transactions = filter_transactions_by_date(
        transactions, date_time
    )

    return {
        "greeting": get_greeting(date_time),
        "cards": get_cards_summary(filt_transactions),
        "top_transactions": get_top_transactions(filt_transactions),
        "currency_rates": get_currency_rates(),
        "stock_prices": get_stock_prices(),
    }



