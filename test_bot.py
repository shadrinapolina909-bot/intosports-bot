import asyncio
from telegram.ext import Application

TOKEN = "8916527707:AAGocCsvT8gPLrRkpTGXJkTP-sWOozsJ6pQ"

async def main():
    app = Application.builder().token(TOKEN).build()
    print("✅ Бот инициализирован!")
    await app.start()
    print("✅ Бот подключился к Telegram!")

if __name__ == '__main__':
    asyncio.run(main())
