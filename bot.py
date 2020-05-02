from telegram.ext import Updater
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import CommandHandler
from telegram import ReplyKeyboardRemove
from telegram import ReplyKeyboardMarkup
from kinopoisk.movie import Movie
from kinopoisk.person import Person
import pymorphy2

# Токен; постоянная, которая запоминает выбор пользователя; все клавиатуры, которые будут использованы
TOKEN = '1114970740:AAE7Mh_vIThMfR0FR7lZcCQMEu_jUl1A6Tk'
constant = None
# Основная клавиатура, выбор между поиском фильма и персоны
reply_keyboardmain = [['Найти фильм по названию', 'Найти информацию об актёре']]
markup_mainkeyboard = ReplyKeyboardMarkup(reply_keyboardmain, one_time_keyboard=False, resize_keyboard=True)
# Если при поиске фильм только один или пользователь выбрали один среди нескольких, то появляется эта клавиатура
reply_keyboardchosenfilm = [['Полное описание', 'Выбрать что-то одно']]
markup_film = ReplyKeyboardMarkup(reply_keyboardchosenfilm, one_time_keyboard=False, resize_keyboard=True)
# При нажатии "Выбрать что-то одно" появляется эта клавиатура с детальным выбором
reply_keyboarddetail = [['Сюжет фильма', 'Длительность фильма', 'Слоган'],
                        ['Рейтинг фильма', 'Год создания', 'Посмотреть постер']]
markup_film_detail = ReplyKeyboardMarkup(reply_keyboarddetail, one_time_keyboard=False, resize_keyboard=True)
#
reply_keyboard4 = [[], []]
markup_actor = ReplyKeyboardMarkup(reply_keyboard4, one_time_keyboard=False, resize_keyboard=True)
# Клавиатура, которая появляется, когда выбирать нечего, например, при вводе названия
reply_keyboardback = [['Вернуться к началу']]
markup_back = ReplyKeyboardMarkup(reply_keyboardback, one_time_keyboard=False, resize_keyboard=True)
# Когда объектов больше пяти, для их выбора появляется клавиатура
reply_keyboardmorethan5 = [['1', '2', '3'], ['4', '5', '>']]
markup_morethanfive = ReplyKeyboardMarkup(reply_keyboardmorethan5, one_time_keyboard=False, resize_keyboard=True)
# Когда объектов больше десяти, для их выбора появляется клавиатура
reply_keyboardmorethan10 = [['<', '6', '7'], ['8', '9', '10']]
markup_morethanten = ReplyKeyboardMarkup(reply_keyboardmorethan10, one_time_keyboard=False, resize_keyboard=True)


# Секретная функция удаления клавиатуры, на всякий случай
def close_keyboard(update, context):
    update.message.reply_text("Убираю клавиатуру.", reply_markup=ReplyKeyboardRemove())


# Функция для старта
def start(update, context):
    update.message.reply_text(
        "Здравствуйте. Этот бот поможет вам получить информацию с сайта КиноПоиск в Телеграм."
        "Выберите команду на клавиатуре.", reply_markup=markup_mainkeyboard)


# Все текстовые сообщения обрабатывает эта функция
def messages(update, context):
    global constant
    mes = update.message.text.lower()
    if constant == 'film_search':
        movie_list = Movie.objects.search(mes)
        if len(movie_list) == 0:
            update.message.reply_text('Извините, фильма с таким названием не найдено. Вернёмся к началу.',
                                      reply_markup=markup_mainkeyboard)
            constant = None
        elif len(movie_list) == 1:
            update.message.reply_text(
                'Найден один фильм. Его полное название - {}. Выберите, что вы хотите узнать.'.format(
                    movie_list[0].title), reply_markup=markup_film)
            constant = None
        elif len(movie_list) > 1:
            comment = pymorphy2.parse('фильм')[0]
            if len(movie_list) >= 6:
                res = 'Найдено {} {}. Вот первые 5 из них:\n'.format(len(movie_list),
                                                                     comment.make_agree_with_number(
                                                                         len(movie_list)).word)
                for i in range(6):
                    res += movie_list[i].title + '\n'
            else:
                res = 'Найдено {} {}. Вот они:\n'.format(len(movie_list),
                                                         comment.make_agree_with_number(
                                                             len(movie_list)).word)
                for i in range(movie_list):
                    res += movie_list[i].title + '\n'
            res += 'Выберите один с помощью клавиатуры.'
            if len(movie_list) >= 5:
                update.message.reply_text(res, reply_markup=markup_morethanfive)
        return
    elif constant == 'actor_search':
        actor_list = Person.objects.search(mes)
        if len(actor_list) == 0:
            update.message.reply_text('Извините, актёра с таким именем найти не удалось. Вернёмся к началу.',
                                      reply_markup=markup_mainkeyboard)
        elif len(actor_list) == 1:
            update.message.reply_text(
                'Полное имя актёра - {}. Выберите, что вы хотите узнать.'.format(
                    actor_list[0].name), reply_markup=markup_actor)
        return
    if mes == 'найти фильм по названию':
        update.message.reply_text('Введите название фильма на русском или английском языке.', reply_markup=markup_back)
        constant = 'film_search'
    elif mes == 'найти информацию об актёре':
        update.message.reply_text('Введите название фильма на русском или английском языке.', reply_markup=markup_back)
        constant = 'actor_search'
    elif mes == 'вернуться к началу':
        update.message.reply_text("Хорошо, вернёмся назад.", reply_markup=reply_keyboardmain)


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text, messages))  # Все текстовые сообщения принимаются здесь
    dp.add_handler(CommandHandler("close_keyboard", close_keyboard))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
