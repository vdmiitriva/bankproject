from src.utils import load_transactions


def main() -> None:
    transactions = load_transactions()

    print("Данные загружены.")
    print(f"Количество операций: {len(transactions)}")

    print("\nДоступные функции:")
    print("Главная страница: get_main_page(date_time, transactions)")
    print("Поиск операций: simple_search(transactions, query)")
    print("Отчёт по дням недели: spending_by_weekday(transactions)")


if __name__ == "__main__":
    main()
