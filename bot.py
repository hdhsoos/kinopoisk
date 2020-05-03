from telegram.ext import Updater
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import CommandHandler
from file import TOKEN
from keyboards import close_keyboard
from commands import start, messages


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("close_keyboard", close_keyboard))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, messages))  # Все текстовые сообщения принимаются здесь
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
