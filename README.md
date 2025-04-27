# 💸 Telegram Expense Tracker Bot

> 🚧 **Note:** This project is currently **in progress**. Database integration is not complete yet, but it's actively being developed.

## 📌 Project Overview

This project is a **Telegram Bot** that allows users to **track their expenses** directly from their Telegram chat. Users can add expenses, view summaries, generate reports, and categorize spending, all using simple bot commands.

---

## 🛠️ Tools and Technologies

- **Programming Language**: Python
- **Telegram API**: Accessed via the `python-telegram-bot` library
- **Database**: PostgreSQL *(integration in progress)*
- **Visualization (optional)**: `matplotlib` or `plotly` for charts *(coming soon)*
- **Hosting/Deployment**: Can be deployed on platforms like Heroku, Render, or run locally

---

## 🧩 Project Features

1. ✅ Add an expense
2. 📊 View summary (daily, weekly, monthly, total)
3. 📁 Export expenses as CSV
4. 🧾 Categorize expenses
5. 🛠️ Database integration *(in progress)*
6. 👤 Per-user tracking *(in progress)*
7. 📉 Generate charts *(coming soon)*

---

## 📦 Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd telegram-expense-tracker
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up your environment variables in the `.env` file:
   ```
   TELEGRAM_BOT_TOKEN=<your-telegram-bot-token>
   DATABASE_URL=<your-database-url>  # not required until DB integration is complete
   ```

5. Run the bot:
   ```
   python bot/main.py
   ```

---

## 📄 Usage

- Use commands in the Telegram chat to interact with the bot.
- For a list of available commands, type `/help`.

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

---