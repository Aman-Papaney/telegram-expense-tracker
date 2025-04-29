from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from utils import start_message, get_db_connection, help_message
import csv
import os
import matplotlib.pyplot as plt
from io import BytesIO


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(start_message())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Provide a list of available commands and their descriptions."""

    await update.message.reply_text(help_message())

async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(context.args[0])
        user = update.effective_user

        # Predefined categories
        predefined_categories = [
            "Groceries",
            "Dining",
            "Transport",
            "Housing",
            "Entertainment",
            "Shopping",
            "Health",
            "Education",
            "Gifts",
            "Savings"
        ]


        # Show category selection buttons (2 buttons per row)
        keyboard = [
            [InlineKeyboardButton(predefined_categories[i], callback_data=f"add_{predefined_categories[i]}"),
             InlineKeyboardButton(predefined_categories[i + 1], callback_data=f"add_{predefined_categories[i + 1]}")]
            for i in range(0, len(predefined_categories), 2)
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Store the amount in user_data for later use
        context.user_data['amount'] = amount

        await update.message.reply_text("Select a category to choose from:", reply_markup=reply_markup)
    except (IndexError, ValueError):
        await update.message.reply_text("⚠️ Usage: /add <amount>")
    except Exception as e:
        await update.message.reply_text(f"❌ An error occurred: {e}")

async def category_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category = query.data.replace("add_", "")
    amount = context.user_data.get('amount')
    user = query.from_user

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Ensure user exists in the database
            cur.execute(
                """
                INSERT INTO users (telegram_id, username)
                VALUES (%s, %s)
                ON CONFLICT (telegram_id) DO NOTHING
                RETURNING id;
                """,
                (user.id, user.first_name)
            )
            result = cur.fetchone()

            if result is None:
                # User already exists, fetch their ID
                cur.execute("SELECT id FROM users WHERE telegram_id = %s;", (user.id,))
                user_id = cur.fetchone()["id"]
            else:
                user_id = result["id"]

            # Insert expense
            cur.execute(
                """
                INSERT INTO expenses (user_id, amount, category)
                VALUES (%s, %s, %s);
                """,
                (user_id, amount, category)
            )

    await query.edit_message_text(f"✅ You spent ${amount} for {category}")

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Fetch user ID
                cur.execute("SELECT id FROM users WHERE telegram_id = %s;", (user.id,))
                user_id = cur.fetchone()["id"]

                # Fetch expenses summary
                cur.execute(
                    """
                    SELECT category, SUM(amount) as total
                    FROM expenses
                    WHERE user_id = %s
                    GROUP BY category;
                    """,
                    (user_id,)
                )
                category_totals = cur.fetchall()

                # Fetch total expenses
                cur.execute(
                    """
                    SELECT SUM(amount) as total
                    FROM expenses
                    WHERE user_id = %s;
                    """,
                    (user_id,)
                )
                total = cur.fetchone()["total"]

        # Prepare the summary message
        message = "💰 Expense Summary:\n\n"
        for row in category_totals:
            message += f"{row['category']}: ${row['total']:.2f}\n"
        message += f"\nTotal: ${total:.2f}"

        await update.message.reply_text(message)
    except Exception as e:
        await update.message.reply_text(f"❌ An error occurred: {e}")

async def export_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Fetch user ID
                cur.execute("SELECT id FROM users WHERE telegram_id = %s;", (user.id,))
                user_id = cur.fetchone()["id"]

                # Fetch user-specific expenses
                cur.execute(
                    """
                    SELECT amount, category, description, date
                    FROM expenses
                    WHERE user_id = %s
                    ORDER BY date;
                    """,
                    (user_id,)
                )
                expenses = cur.fetchall()

        # Write expenses to a temporary CSV file
        temp_file = f"{user.id}_expenses.csv"
        with open(temp_file, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Amount", "Category", "Description", "Date"])
            for expense in expenses:
                writer.writerow([expense["amount"], expense["category"], expense["description"], expense["date"]])

        # Send the CSV file to the user
        await update.message.reply_document(
            document=open(temp_file, "rb"),
            filename="expenses.csv",
            caption="Here is your expenses file."
        )

        # Clean up the temporary file
        os.remove(temp_file)
    except Exception as e:
        await update.message.reply_text(f"❌ An error occurred: {e}")

async def daily_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    today = datetime.now().date()

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Fetch user ID
                cur.execute("SELECT id FROM users WHERE telegram_id = %s;", (user.id,))
                user_id = cur.fetchone()["id"]

                # Fetch daily expenses
                cur.execute(
                    """
                    SELECT category, SUM(amount) as total
                    FROM expenses
                    WHERE user_id = %s AND date::date = %s
                    GROUP BY category;
                    """,
                    (user_id, today)
                )
                category_totals = cur.fetchall()

                # Fetch total daily expenses
                cur.execute(
                    """
                    SELECT SUM(amount) as total
                    FROM expenses
                    WHERE user_id = %s AND date::date = %s;
                    """,
                    (user_id, today)
                )
                total = cur.fetchone()["total"]

        # Prepare the daily summary message
        message = "📅 Today's Expenses:\n\n"
        for row in category_totals:
            message += f"{row['category']}: ${row['total']:.2f}\n"
        message += f"\nTotal: ${total:.2f}"

        await update.message.reply_text(message)
    except Exception as e:
        await update.message.reply_text(f"❌ An error occurred: {e}")

async def weekly_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Fetch user ID
                cur.execute("SELECT id FROM users WHERE telegram_id = %s;", (user.id,))
                user_id = cur.fetchone()["id"]

                # Fetch weekly expenses
                cur.execute(
                    """
                    SELECT category, SUM(amount) as total
                    FROM expenses
                    WHERE user_id = %s AND date::date BETWEEN %s AND %s
                    GROUP BY category;
                    """,
                    (user_id, week_start, today)
                )
                category_totals = cur.fetchall()

                # Fetch total weekly expenses
                cur.execute(
                    """
                    SELECT SUM(amount) as total
                    FROM expenses
                    WHERE user_id = %s AND date::date BETWEEN %s AND %s;
                    """,
                    (user_id, week_start, today)
                )
                total = cur.fetchone()["total"]

        # Prepare the weekly summary message
        message = "📅 This Week's Expenses:\n\n"
        for row in category_totals:
            message += f"{row['category']}: ${row['total']:.2f}\n"
        message += f"\nTotal: ${total:.2f}"

        await update.message.reply_text(message)
    except Exception as e:
        await update.message.reply_text(f"❌ An error occurred: {e}")

async def monthly_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    today = datetime.now().date()
    month_start = today.replace(day=1)

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Fetch user ID
                cur.execute("SELECT id FROM users WHERE telegram_id = %s;", (user.id,))
                user_id = cur.fetchone()["id"]

                # Fetch monthly expenses
                cur.execute(
                    """
                    SELECT category, SUM(amount) as total
                    FROM expenses
                    WHERE user_id = %s AND date::date BETWEEN %s AND %s
                    GROUP BY category;
                    """,
                    (user_id, month_start, today)
                )
                category_totals = cur.fetchall()

                # Fetch total monthly expenses
                cur.execute(
                    """
                    SELECT SUM(amount) as total
                    FROM expenses
                    WHERE user_id = %s AND date::date BETWEEN %s AND %s;
                    """,
                    (user_id, month_start, today)
                )
                total = cur.fetchone()["total"]

        # Prepare the monthly summary message
        message = "📅 This Month's Expenses:\n\n"
        for row in category_totals:
            message += f"{row['category']}: ${row['total']:.2f}\n"
        message += f"\nTotal: ${total:.2f}"

        await update.message.reply_text(message)
    except Exception as e:
        await update.message.reply_text(f"❌ An error occurred: {e}")

async def generate_expense_pie_chart(user_id: int):
    """Generates a pie chart of expenses grouped by category for a given user."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Query expenses grouped by category
            cur.execute(
                """
                SELECT category, SUM(amount) as total
                FROM expenses
                WHERE user_id = %s
                GROUP BY category;
                """,
                (user_id,)
            )
            results = cur.fetchall()

    if not results:
        return None

    # Extract data for the pie chart
    categories = [row['category'] for row in results]
    totals = [row['total'] for row in results]

    # Create the pie chart
    plt.figure(figsize=(6, 6))
    plt.pie(totals, labels=categories, autopct='%1.1f%%', startangle=140)
    plt.title('Expenses by Category')

    # Save the chart to a BytesIO object
    chart_stream = BytesIO()
    plt.savefig(chart_stream, format='png')
    plt.close()
    chart_stream.seek(0)

    return chart_stream

async def chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Fetch user ID
                cur.execute("SELECT id FROM users WHERE telegram_id = %s;", (user.id,))
                user_id = cur.fetchone()["id"]

        # Generate the pie chart
        chart_stream = await generate_expense_pie_chart(user_id)

        if chart_stream is None:
            await update.message.reply_text("No expenses to show yet.")
        else:
            await update.message.reply_photo(photo=chart_stream, caption="Here is your expense chart.")
    except Exception as e:
        await update.message.reply_text(f"❌ An error occurred: {e}")
