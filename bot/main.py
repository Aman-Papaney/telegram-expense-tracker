import os
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from dotenv import load_dotenv
from handlers import (
    start, add_expense, category_selected, summary,
    export_expenses, daily_summary, weekly_summary, monthly_summary, help_command,
    #  delete_category, show_categories, handle_delete_category  # Import new handler
    # add_category, delete_category, show_categories, handle_delete_category  # Import new handler
)

load_dotenv()

# Initialize bot
app = ApplicationBuilder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add_expense))
app.add_handler(CommandHandler("summary", summary))
app.add_handler(CommandHandler("export", export_expenses))
app.add_handler(CommandHandler("daily", daily_summary))
app.add_handler(CommandHandler("weekly", weekly_summary))
app.add_handler(CommandHandler("monthly", monthly_summary))
app.add_handler(CommandHandler("help", help_command))
# app.add_handler(CommandHandler("add_category", add_category))
# app.add_handler(CommandHandler("delete_category", delete_category))
# app.add_handler(CommandHandler("show_categories", show_categories))

# app.add_handler(CallbackQueryHandler(handle_delete_category, pattern="^delete_*"))
app.add_handler(CallbackQueryHandler(category_selected, pattern="^add_*"))

print("BOT STARTED  ")

app.run_polling()
