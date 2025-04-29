import csv
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

# EXPENSES_FILE = "expenses.csv"


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

def start_message():
    msg = """🎉 Hey there, spender! Welcome to Expense Tracker Bot!

Ready to take control of your wallet without breaking a sweat?
I’m your budgeting buddy — here to track your expenses, show you where your money’s going, and throw in some charts for good measure. 📊

Just say something like /add 50 and boom 💥 — logged!
Want summaries? I’ve got ‘em. Charts? You bet. CSV exports? Fancy!

Need a quick tour? Just type /help and I’ll show you the ropes.

Let’s make money tracking actually fun. 💸😎"""


    return msg

def help_message():
    msg = (
        "Here are the available commands:\n\n"
        "/start - Start the bot and get a welcome message.\n"
        "/add <amount> - Add a new expense. Example: /add 50\n"
        "/summary - Get a summary of all expenses.\n"
        "/daily - Get today's expenses.\n"
        "/weekly - Get this week's expenses.\n"
        "/monthly - Get this month's expenses.\n"
        "/export - Export all expenses as a CSV file.\n"
        "/help - Show this help message.\n"
        "/chart - Show expenses in pie chart.\n"
    )


    return msg
