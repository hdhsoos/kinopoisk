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
TOKEN = '1246543622:AAGV4wEzLqINoUKufPCU_KaMfAcfwg1KUgk'
constant = None
# Основная клавиатура, выбор между поиском фильма и персоны
reply_keyboardmain = [['Найти фильм по названию', 'Найти информацию о знаменитости']]
markup_main_keyboard = ReplyKeyboardMarkup(reply_keyboardmain, one_time_keyboard=False, resize_keyboard=True)
# Клавиатура, которая появляется, когда выбирать нечего, например, при вводе названия
reply_keyboardback = [['Вернуться к началу']]
markup_back = ReplyKeyboardMarkup(reply_keyboardback, one_time_keyboard=False, resize_keyboard=True)
# Когда объектов больше пяти, для их выбора появляется эта клавиатура
reply_keyboardmorethan5 = [['1', '2', '3'], ['4', '5', '>']]
markup_morethanfive = ReplyKeyboardMarkup(reply_keyboardmorethan5, one_time_keyboard=False, resize_keyboard=True)
# Когда объектов больше десяти, для их выбора появляется эта клавиатура
reply_keyboardmorethan10 = [['<', '6', '7'], ['8', '9', '10']]
markup_morethanten = ReplyKeyboardMarkup(reply_keyboardmorethan10, one_time_keyboard=False, resize_keyboard=True)
# Когда объектов пять, для их выбора появляется эта клавиатура
reply_keyboardmorethan5 = [['1', '2'], ['3', '4', '5']]
markup_five = ReplyKeyboardMarkup(reply_keyboardmorethan5, one_time_keyboard=False, resize_keyboard=True)


# Секретная функция удаления клавиатуры, на всякий случай
def close_keyboard(update, context):
    update.message.reply_text("Убираю клавиатуру.", reply_markup=ReplyKeyboardRemove())


# Функция для старта
def start(update, context):
    update.message.reply_text(
        "Здравствуйте. Этот бот поможет вам получить информацию с сайта КиноПоиск в Телеграм. "
        "Выберите команду на клавиатуре.", reply_markup=markup_main_keyboard)


# Все текстовые сообщения обрабатывает эта функция
def messages(update, context):
    global constant
    # Используем переменную для хранения сообщения в нижнем регистре
    mes = update.message.text.lower()
    print(mes)
    # Так как название фильма не постоянная команда, когда мы узнаём,
    # что пользователь сейчас выберет фильм, мы меняем постоянную, а затем
    # понимаем, что непонятное словосочетание - фильм (или актёр).
    # При возвращении назад мы "обнуляем" постоянную.
    if mes == 'найти фильм по названию' and constant is None:
        update.message.reply_text('Введите название фильма на русском или английском языке.', reply_markup=markup_back)
        constant = 'film_search'
    elif mes == 'найти информацию о знаменитости' and constant is None:
        update.message.reply_text('Введите имя знаменитости на русском или английском языке.', reply_markup=markup_back)
        constant = 'actor_search'
    elif mes == 'вернуться к началу':
        update.message.reply_text("Хорошо, вернёмся.", reply_markup=markup_main_keyboard)
        constant = None
    elif constant == 'film_search':
        constant = None
        movie_list = Movie.objects.search(mes)
        length = len(movie_list)  # Чтобы постоянно не пересчитывать длину функции
        if length == 0:
            update.message.reply_text('Извините, фильма с таким названием не найдено. Вернёмся к началу.',
                                      reply_markup=markup_main_keyboard)
        elif length > 1:
            n = length if length <= 10 else 10
            comment = 'фильм'
            # comment = pymorphy2.parse('фильм')[0] .make_agree_with_number(length).word
            res = 'Найдено {} {}. Вот {} из них:\n'.format(length, comment, n)
            for i in range(n):
                res += movie_list[i].title + '\n'
            res += 'Выберите один с помощью клавиатуры.'
            reply_keyboardfilms = [[i + 1 for i in range(n // 2)], [i + 1 for i in range(n // 2, n)]]
            markupfilmskeyboard = ReplyKeyboardMarkup(reply_keyboardfilms, one_time_keyboard=False,
                                                      resize_keyboard=True)
            update.message.reply_text(res, reply_markup=markupfilmskeyboard)
            constant = ['film chosen', movie_list]
        elif length == 1:
            update.message.reply_text(
                'Найден один фильм. Полное название - {}.\n{}\nСлоган - {}\nГод - {}\nДлительность - {}\nРейтинг фильма - {}'.format(
                    movie_list[0].title, movie_list[0].plot, movie_list[0].tagline,
                    movie_list[0].year, movie_list[0].runtime, movie_list[0].rating), reply_markup=markup_main_keyboard)
    elif constant == 'actor_search':
        actor_list = Person.objects.search(mes)
        length = len(actor_list)
        if length == 0:
            update.message.reply_text('Извините, знаменитости с таким именем найти не удалось. Вернёмся к началу.',
                                      reply_markup=markup_main_keyboard)
        elif length == 1:
            update.message.reply_text(
                'Имя - {}. '.format(
                    actor_list[0].name), reply_markup=markup_main_keyboard)
        elif length > 1:
            n = length if length <= 10 else 10
            comment = 'знаменитость'
            #comment = pymorphy2.parse('знаменитость')[0].make_agree_with_number(length).word
            res = 'Найдено {} {}. Вот {} из них:\n'.format(length,
                                                           comment, n)
            for i in range(n):
                res += actor_list[i].name + '\n'
            res += 'Выберите одного с помощью клавиатуры.'
            reply_keyboardactors = [[i + 1 for i in range(n // 2)], [i + 1 for i in range(n // 2, n)]]
            markupactorskeyboard = ReplyKeyboardMarkup(reply_keyboardactors, one_time_keyboard=False,
                                                       resize_keyboard=True)
            update.message.reply_text(res, reply_markup=markupactorskeyboard)
            constant = ['actor chosen', actor_list]
    elif constant[0] == 'actor chosen':
        i = mes
        actor = constant[1][i]
        update.message.reply_text(
            '{}\n{}-{}'.format(actor.name, actor.year_birth, actor.year_death), reply_markup=markup_main_keyboard)
    elif constant[0] == 'film chosen':
        i = mes
        movie = constant[1][i]
        update.message.reply_text(
            'Полное название - {}.\n{}\nСлоган - {}\nГод - {}\nДлительность - {}\nРейтинг фильма - {}'.format(
                movie.title, movie.plot, movie.tagline,
                movie.year, movie.runtime, movie.rating), reply_markup=markup_main_keyboard)


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
