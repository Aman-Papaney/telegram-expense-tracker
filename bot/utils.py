import csv
import os

EXPENSES_FILE = "expenses.csv"


def load_expenses():
    """Load expenses from the CSV file."""
    if os.path.exists(EXPENSES_FILE):
        with open(EXPENSES_FILE, mode="r", newline="") as file:
            reader = csv.reader(file)
            return [(float(row[0]), row[1], row[2]) for row in reader]
    return []


def save_expense(expenses, amount, category, date):
    """Save a new expense to the CSV file."""
    expenses.append((amount, category, date))
    with open(EXPENSES_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([amount, category, date])


def start_message():
    msg = """👋 Welcome to Expense Tracker Bot!
Your personal finance buddy, right inside Telegram.

Track your expenses with categories and dates – effortlessly.
🛠️ What You Can Do:

➕ Add an expense:
/add 50 groceries – Adds a $50 expense under "groceries" with today’s date

📊 Get summaries:

    /summary – Total + category breakdown

    /daily, /weekly, /monthly – See your spending by time period

📂 View by category:
/category groceries – See all expenses in the "groceries" category

📤 Export your data:
/export – Get a downloadable CSV of all expenses with date & category

🆘 Need help?
/help – List of all available commands

➕ Manage categories:
    /addcategory <name> – Add a new category
    /deletecategory <name> – Delete an existing category
    /categories – Show all existing categories"""


    return msg
