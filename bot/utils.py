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
    msg = """🎉 Hey there, spender! Welcome to Expense Tracker Bot!

Ready to take control of your wallet without breaking a sweat?
I’m your budgeting buddy — here to track your expenses, show you where your money’s going, and throw in some charts for good measure. 📊

Just say something like add 50 and boom 💥 — logged!
Want summaries? I’ve got ‘em. Charts? You bet. CSV exports? Fancy!

Need a quick tour? Just type /help and I’ll show you the ropes.

Let’s make money tracking actually fun. 💸😎"""


    return msg
