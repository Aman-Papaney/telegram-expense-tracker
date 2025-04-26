from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from utils import load_expenses, save_expense, start_message, get_db_connection
import csv
import os

expenses = load_expenses()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(start_message())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Provide a list of available commands and their descriptions."""
    help_text = (
        "Here are the available commands:\n\n"
        "/start - Start the bot and get a welcome message.\n"
        "/add <amount> - Add a new expense. Example: /add 50\n"
        "/summary - Get a summary of all expenses.\n"
        "/daily - Get today's expenses.\n"
        "/weekly - Get this week's expenses.\n"
        "/monthly - Get this month's expenses.\n"
        "/export - Export all expenses as a CSV file.\n"
        "/help - Show this help message.\n"
        # "/add_category <name> - Add a new category.\n"
        # "/delete_category - Delete an existing category.\n"
        # "/show_categories - Display all existing categories."
    )
    await update.message.reply_text(help_text)

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

# async def add_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     try:
#         new_category = " ".join(context.args).strip()
#         if not new_category:
#             raise ValueError("Category name cannot be empty.")
#         if new_category in CATEGORIES:
#             await update.message.reply_text(f"⚠️ The category '{new_category}' already exists.")
#         else:
#             CATEGORIES.append(new_category)
#             await update.message.reply_text(f"✅ Category '{new_category}' added successfully.")
#     except Exception as e:
#         await update.message.reply_text(f"❌ Error: {e}")

# async def delete_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Provide a list of categories for the user to choose from for deletion."""
#     predefined_categories = ["Travel", "Food", "Clothes", "Entertainment", "Health"]

#     if not predefined_categories:
#         await update.message.reply_text("⚠️ No categories available to delete.")
#         return

#     # Show category selection buttons
#     keyboard = [[InlineKeyboardButton(cat, callback_data=f"delete_{cat}")] for cat in predefined_categories]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     await update.message.reply_text("Select a category to delete:", reply_markup=reply_markup)

# async def handle_delete_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handle the deletion of a selected category."""
#     query = update.callback_query
#     await query.answer()

#     predefined_categories = ["Travel", "Food", "Clothes", "Entertainment", "Health"]
#     category_to_delete = query.data.replace("delete_", "")

#     if category_to_delete in predefined_categories:
#         predefined_categories.remove(category_to_delete)
#         await query.edit_message_text(f"✅ Category '{category_to_delete}' deleted successfully.")
#     else:
#         await query.edit_message_text(f"❌ Category '{category_to_delete}' does not exist.")


# async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Show all existing categories."""
#     if CATEGORIES:
#         categories_list = "\n".join(f"- {category}" for category in CATEGORIES)
#         await update.message.reply_text(f"📂 Existing Categories:\n{categories_list}")
#     else:
#         await update.message.reply_text("⚠️ No categories available.")
