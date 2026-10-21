import pandas as pd
import pytest

from src.reports import save_report, spending_by_weekday


def test_spending_by_weekday_returns_seven_days(report_transactions):
    result = spending_by_weekday(report_transactions, "2021-12-31")

    assert len(result) == 7
    assert result["День недели"].tolist() == [
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
        "Воскресенье",
    ]


def test_spending_by_weekday_calculates_expenses(report_transactions):
    result = spending_by_weekday(report_transactions, "2021-12-31")

    friday = result.loc[
        result["День недели"] == "Пятница",
        "Средние расходы",
    ].iloc[0]

    assert friday == pytest.approx(1000 / 14)


def test_spending_by_weekday_without_ok_transactions(report_transactions):
    transactions = report_transactions.copy()
    transactions["Статус"] = "FAILED"

    result = spending_by_weekday(transactions, "2021-12-31")

    assert len(result) == 7
    assert (result["Средние расходы"] == 0).all()


def test_spending_by_weekday_without_expenses(report_transactions):
    transactions = report_transactions.copy()
    transactions["Сумма платежа"] = 1

    result = spending_by_weekday(transactions, "2021-12-31")

    assert len(result) == 7
    assert (result["Средние расходы"] == 0).all()


def test_spending_by_weekday_excludes_other_currency(report_transactions):
    transactions = report_transactions.copy()
    transactions.loc[transactions["Валюта платежа"] == "RUB", "Сумма платежа"] = 0

    result = spending_by_weekday(transactions, "2021-12-31")

    friday = result.loc[
        result["День недели"] == "Пятница",
        "Средние расходы",
    ].iloc[0]

    assert friday == 0


def test_spending_by_weekday_sums_expenses_on_same_day():
    transactions = pd.DataFrame(
        {
            "Дата операции": ["31.12.2021", "31.12.2021"],
            "Статус": ["OK", "OK"],
            "Валюта платежа": ["RUB", "RUB"],
            "Сумма платежа": [-1000, -500],
        }
    )

    result = spending_by_weekday(transactions, "2021-12-31")

    friday = result.loc[
        result["День недели"] == "Пятница",
        "Средние расходы",
    ].iloc[0]

    assert friday == pytest.approx(1500 / 14)


def test_spending_by_weekday_excludes_expenses_before_period():
    transactions = pd.DataFrame(
        {
            "Дата операции": ["29.09.2021"],
            "Статус": ["OK"],
            "Валюта платежа": ["RUB"],
            "Сумма платежа": [-5000],
        }
    )

    result = spending_by_weekday(transactions, "2021-12-31")

    assert (result["Средние расходы"] == 0).all()


def test_spending_by_weekday_does_not_modify_original(report_transactions):
    original = report_transactions.copy(deep=True)

    spending_by_weekday(report_transactions, "2021-12-31")

    pd.testing.assert_frame_equal(report_transactions, original)


def test_save_report_uses_default_filename(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    @save_report
    def example_report():
        return pd.DataFrame({"Расход": [100, 200]})

    result = example_report()

    assert (tmp_path / "report.csv").exists()
    pd.testing.assert_frame_equal(
        pd.read_csv(tmp_path / "report.csv"),
        result,
    )


def test_save_report_uses_custom_filename(tmp_path):
    output_file = tmp_path / "custom_report.csv"

    @save_report(str(output_file))
    def example_report():
        return pd.DataFrame({"Расход": [100, 200]})

    result = example_report()

    assert output_file.exists()
    pd.testing.assert_frame_equal(
        pd.read_csv(output_file),
        result,
    )


def test_spending_by_weekday_includes_start_of_period():
    transactions = pd.DataFrame(
        {
            "Дата операции": [
                "30.09.2021",
                "01.10.2021",
            ],
            "Статус": ["OK", "OK"],
            "Валюта платежа": ["RUB", "RUB"],
            "Сумма платежа": [-700, -300],
        }
    )

    result = spending_by_weekday(transactions, "2021-12-31")

    thursday = result.loc[
        result["День недели"] == "Четверг",
        "Средние расходы",
    ].iloc[0]

    assert thursday == pytest.approx(700 / 14)


def test_spending_by_weekday_uses_default_date(
    report_transactions, tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)

    result = spending_by_weekday(report_transactions)

    assert len(result) == 7
    assert result["День недели"].tolist() == [
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
        "Воскресенье",
    ]
