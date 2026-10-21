from functools import wraps
from typing import Optional

import pandas as pd


def save_report(func=None, filename="report.csv"):
    if isinstance(func, str):
        filename = func
        func = None

    if func is None:
        return lambda report_func: save_report(report_func, filename)

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        result.to_csv(filename, index=False, encoding="utf-8-sig")
        return result

    return wrapper


@save_report("spending_by_weekday.csv")
def spending_by_weekday(
    transactions: pd.DataFrame, date: Optional[str] = None
) -> pd.DataFrame:
    transactions_copy = transactions.copy()
    transactions_copy["Дата операции"] = pd.to_datetime(
        transactions_copy["Дата операции"], dayfirst=True
    )
    expenses = transactions_copy[
        (transactions_copy["Статус"] == "OK")
        & (transactions_copy["Валюта платежа"] == "RUB")
        & (transactions_copy["Сумма платежа"] < 0)
    ].copy()

    if date is None:
        date = pd.Timestamp.today()
    else:
        date = pd.to_datetime(date, format="%Y-%m-%d")

    end_date = pd.Timestamp(date).normalize()
    end_exclusive = end_date + pd.Timedelta(days=1)
    start_date = (end_date - pd.DateOffset(months=3)).normalize()

    expenses_3_months = expenses[
        (expenses["Дата операции"] >= start_date)
        & (expenses["Дата операции"] < end_exclusive)
    ].copy()
    expenses_3_months["Расход"] = -expenses_3_months["Сумма платежа"]

    daily_expenses = expenses_3_months.groupby(
        expenses_3_months["Дата операции"].dt.date
    )["Расход"].sum()

    daily_expenses.index = pd.to_datetime(daily_expenses.index)
    daily_expenses = daily_expenses.reindex(
        pd.date_range(start=start_date, end=end_date, freq="D"), fill_value=0
    )
    daily_expenses = daily_expenses.groupby(daily_expenses.index.dayofweek).mean()
    daily_expenses = daily_expenses.reset_index()

    weekday_names = {
        0: "Понедельник",
        1: "Вторник",
        2: "Среда",
        3: "Четверг",
        4: "Пятница",
        5: "Суббота",
        6: "Воскресенье",
    }

    daily_expenses["index"] = daily_expenses["index"].map(weekday_names)
    daily_expenses = daily_expenses.rename(
        columns={"index": "День недели", "Расход": "Средние расходы"}
    )

    return daily_expenses
