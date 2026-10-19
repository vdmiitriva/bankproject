
from src.utils import load_transactions
from src.views import get_main_page

transactions = load_transactions()

result = get_main_page(
    "2021-12-31 15:00:00",
    transactions,
)

print(result)
