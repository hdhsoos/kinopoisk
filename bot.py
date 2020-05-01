from telegram.ext import Updater
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import CommandHandler
from telegram import ReplyKeyboardRemove
from telegram import ReplyKeyboardMarkup
from kinopoisk.movie import Movie
from kinopoisk.person import Person

TOKEN = '1114970740:AAE7Mh_vIThMfR0FR7lZcCQMEu_jUl1A6Tk'
constant = None


def close_keyboard(update, context):
    update.message.reply_text("Убираю клавиатуру.", reply_markup=ReplyKeyboardRemove())


def start(update, context):
    update.message.reply_text(
        "Здравствуйте. Этот бот поможет вам получить информацию о фильмах с сайта КиноПоиск в Телеграм."
        "Выберите команду на клавиатуре.", reply_markup=markup_mainkeyboard)


def messages(update, context):
    global constant
    mes = update.message.text.lower()
    if constant == 'film_search':
        movie_list = Movie.objects.search(mes)
        if len(movie_list) == 0:
            update.message.reply_text('Извините, фильма с таким названием не найдено.')
        elif len(movie_list) == 1:
            update.message.reply_text(
                'Найден один фильм. Его полное название - {}. Выберите, что вы хотите узнать.'.format(
                    movie_list[0].title), reply_markup=markup_film)
        return
    if constant == 'actor_search':
        actor_list = Person.objects.search(mes)
        if len(actor_list) == 0:
            update.message.reply_text('Извините, актёра с таким именем найти не удалось.')
        elif len(actor_list) == 1:
            update.message.reply_text(
                'Полное имя актёра - {}. Выберите, что вы хотите узнать.'.format(
                    actor_list[0].name), reply_markup=markup_actor)
        return
    if mes == 'найти фильм по названию':
        update.message.reply_text('Введите название фильма на русском или английском языке.', reply_markup=markup_back)
        constant = 'film_search'
    elif mes.lower() == 'Вернуться к началу':
        update.message.reply_text("Хорошо, вернёмся назад.", reply_markup=reply_keyboard1)


reply_keyboard1 = [['Найти фильм по названию', 'Найти информацию об актёре']]
markup_mainkeyboard = ReplyKeyboardMarkup(reply_keyboard1, one_time_keyboard=False, resize_keyboard=True)
reply_keyboard2 = [['Полное описание', 'Выбрать что-то одно']]
markup_film = ReplyKeyboardMarkup(reply_keyboard2, one_time_keyboard=False, resize_keyboard=True)
reply_keyboard3 = [['Сюжет фильма', 'Длительность фильма', 'Слоган'],
                   ['Рейтинг фильма', 'Год создания', 'Посмотреть постер']]
markup_film_detail = ReplyKeyboardMarkup(reply_keyboard3, one_time_keyboard=False, resize_keyboard=True)
reply_keyboard4 = [[], []]
markup_actor = ReplyKeyboardMarkup(reply_keyboard4, one_time_keyboard=False, resize_keyboard=True)
reply_keyboard4 = [['Вернуться к началу']]
markup_back = ReplyKeyboardMarkup(reply_keyboard4, one_time_keyboard=False, resize_keyboard=True)


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text, messages))
    dp.add_handler(CommandHandler("close_keyboard", close_keyboard))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
