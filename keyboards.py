# Тут хранятся все клавиатуры, которые будут использованы
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

# Основная клавиатура, выбор между поиском фильма и персоны
reply_keyboardmain = [['Найти фильм по названию', 'Найти информацию о знаменитости']]
markup_main_keyboard = ReplyKeyboardMarkup(reply_keyboardmain, one_time_keyboard=False, resize_keyboard=True)
# Клавиатура, которая появляется, когда выбирать нечего, например, при вводе названия
reply_keyboardback = [['Вернуться к началу']]
markup_back = ReplyKeyboardMarkup(reply_keyboardback, one_time_keyboard=False, resize_keyboard=True)
# Хотите увидеть фильмографию? Хотите увидеть актёрский состав?
reply_keyboardyesornot = [['Да', 'Вернуться к началу']]
markup_yesornot = ReplyKeyboardMarkup(reply_keyboardyesornot, one_time_keyboard=False, resize_keyboard=True)
# Перелистывание страниц
reply_keyboardpages = [['Ещё фильмы', 'Вернуться к началу']]
markup_pages = ReplyKeyboardMarkup(reply_keyboardpages, one_time_keyboard=False, resize_keyboard=True)


# Секретная функция удаления клавиатуры, на всякий случай
def close_keyboard(update, context):
    update.message.reply_text("Убираю клавиатуру.", reply_markup=ReplyKeyboardRemove())
