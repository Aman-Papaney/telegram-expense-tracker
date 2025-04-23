from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from utils import load_expenses, save_expense, start_message

# Predefined categories
CATEGORIES = ["Travel", "Food", "Clothes", "Entertainment", "Health"]

expenses = load_expenses()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(start_message())

async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(context.args[0])
        context.user_data['amount'] = amount

        # Show category selection buttons
        keyboard = [[InlineKeyboardButton(cat, callback_data=cat)] for cat in CATEGORIES]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Select a category:", reply_markup=reply_markup)
    except (IndexError, ValueError):
        await update.message.reply_text("⚠️ Usage: /add <amount>")

async def category_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category = query.data
    amount = context.user_data.get('amount')
    date = datetime.now().strftime("%Y-%m-%d")

    # Save expense
    save_expense(expenses, amount, category, date)

    await query.edit_message_text(f"✅ Added: ${amount} for {category} on {date}")

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Calculate total expenses
    total = sum(e[0] for e in expenses)

    # Calculate expenses by category
    category_totals = {}
    for amount, category, _ in expenses:
        if category in category_totals:
            category_totals[category] += amount
        else:
            category_totals[category] = amount

    # Prepare the summary message
    message = "💰 Expense Summary:\n\n"
    for category, total_amount in category_totals.items():
        message += f"{category}: ${total_amount:.2f}\n"
    message += f"\nTotal: ${total:.2f}"

    await update.message.reply_text(message)

async def export_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Send the expenses.csv file to the user
        await update.message.reply_document(
            document=open("expenses.csv", "rb"),
            filename="expenses.csv",
            caption="Here is your expenses file."
        )
    except Exception as e:
        await update.message.reply_text(f"❌ An error occurred: {e}")

async def daily_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().date()
    daily_expenses = [e[0] for e in expenses if datetime.strptime(e[2], "%Y-%m-%d").date() == today]
    total = sum(daily_expenses)
    await update.message.reply_text(f"📅 Today's expenses: ${total}")

async def weekly_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    weekly_expenses = [e[0] for e in expenses if week_start <= datetime.strptime(e[2], "%Y-%m-%d").date() <= today]
    total = sum(weekly_expenses)
    await update.message.reply_text(f"📅 This week's expenses: ${total}")

async def monthly_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().date()
    month_start = today.replace(day=1)
    monthly_expenses = [e[0] for e in expenses if month_start <= datetime.strptime(e[2], "%Y-%m-%d").date() <= today]
    total = sum(monthly_expenses)
    await update.message.reply_text(f"📅 This month's expenses: ${total}")

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
        "/add_category <name> - Add a new category.\n"
        "/delete_category <name> - Delete an existing category.\n"
        "/show_categories - Display all existing categories."
    )
    await update.message.reply_text(help_text)

async def add_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        new_category = " ".join(context.args).strip()
        if not new_category:
            raise ValueError("Category name cannot be empty.")
        if new_category in CATEGORIES:
            await update.message.reply_text(f"⚠️ The category '{new_category}' already exists.")
        else:
            CATEGORIES.append(new_category)
            await update.message.reply_text(f"✅ Category '{new_category}' added successfully.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def delete_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        category_to_delete = " ".join(context.args).strip()
        if not category_to_delete:
            raise ValueError("Category name cannot be empty.")
        if category_to_delete not in CATEGORIES:
            await update.message.reply_text(f"⚠️ The category '{category_to_delete}' does not exist.")
        else:
            CATEGORIES.remove(category_to_delete)
            await update.message.reply_text(f"✅ Category '{category_to_delete}' deleted successfully.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all existing categories."""
    if CATEGORIES:
        categories_list = "\n".join(f"- {category}" for category in CATEGORIES)
        await update.message.reply_text(f"📂 Existing Categories:\n{categories_list}")
    else:
        await update.message.reply_text("⚠️ No categories available.")
