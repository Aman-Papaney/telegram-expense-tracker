import csv
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

EXPENSES_FILE = "expenses.csv"


def get_db_connection():
    """Establish a connection to the PostgreSQL database."""
    return psycopg2.connect(
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        host=os.getenv("PGHOST"),
        port=os.getenv("DB_PORT"),
        cursor_factory=RealDictCursor,
        sslmode='require' 
    )


def load_expenses():
    """Load expenses from the CSV file and return them as a list of tuples."""
    expenses = []
    try:
        with open(EXPENSES_FILE, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                try:
                    # Ensure the row has the correct number of elements and valid data
                    if len(row) == 3 and row[0] and row[1] and row[2]:
                        expenses.append((float(row[0]), row[1], row[2]))
                except ValueError:
                    # Skip rows with invalid data
                    continue
    except FileNotFoundError:
        # If the file does not exist, return an empty list
        pass

    return expenses


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
