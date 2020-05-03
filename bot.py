from telegram.ext import Updater
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import CommandHandler
from telegram import ReplyKeyboardRemove
from telegram import ReplyKeyboardMarkup
from kinopoisk.movie import Movie
from kinopoisk.person import Person

# Токен; постоянная, которая запоминает выбор пользователя; все клавиатуры, которые будут использованы
TOKEN = '1114970740:AAE7Mh_vIThMfR0FR7lZcCQMEu_jUl1A6Tk'
constant = None
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
        update.message.reply_text(
            'Введите название фильма на русском или английском языке. Информация о сериалах недоступна.',
            reply_markup=markup_back)
        constant = 'film_search'
    elif mes == 'найти информацию о знаменитости' and constant is None:
        update.message.reply_text('Введите имя знаменитости на русском или английском языке.', reply_markup=markup_back)
        constant = 'actor_search'
    elif mes == 'вернуться к началу':
        update.message.reply_text("Хорошо, вернёмся.", reply_markup=markup_main_keyboard)
        constant = None
    elif constant == 'film_search':
        movie_list = Movie.objects.search(mes)
        length = len(movie_list)  # Чтобы постоянно не пересчитывать длину функции
        if length == 0:
            update.message.reply_text('Извините, фильма с таким названием не найдено. Вернёмся к началу.',
                                      reply_markup=markup_main_keyboard)
            constant = None
        elif length >= 1:
            movie = Movie(id=movie_list[0].id)
            movie.get_content('main_page')
            update.message.reply_text(
                'Полное название - {}.\n{}\nСлоган - {}\nГод - {}\nДлительность - {}\nРейтинг фильма - {}\nХотите увидеть список актёров?'.format(
                    movie.title, movie.plot, movie.tagline,
                    movie.year, movie.runtime, movie.rating), reply_markup=markup_yesornot)
            constant = ['cast', movie]
    elif constant[0] == 'cast':
        res = ''
        x = constant[1].actors
        for el in x[:10]:
            res += '\n{}'.format(el)
        if mes == 'вернуться к началу':
            res = 'Хорошо, вернёмся'
        else:
            res = 'В фильме снимались:' + res
        update.message.reply_text(res, reply_markup=markup_main_keyboard)
        constant = None
    elif constant == 'actor_search':
        actor_list = Person.objects.search(mes)
        length = len(actor_list)
        if length == 0:
            update.message.reply_text('Извините, знаменитости с таким именем найти не удалось. Вернёмся к началу.',
                                      reply_markup=markup_main_keyboard)
            constant = None
        elif length >= 1:
            actor = Person(id=actor_list[0].id)
            actor.get_content('main_page')
            update.message.reply_text(
                ('{}, {} год рождения\nХотите увидеть фильмографию?'.format(actor.name, actor.year_birth)),
                reply_markup=markup_yesornot)
            constant = ['filmography', actor]
    elif constant[0] == 'filmography':
        res = ''
        x = constant[1].career['actor']
        x.reverse()
        if len(constant) == 2:
            if len(x) > 10:
                for el in constant[1].career['actor'][:10]:
                    res += '\n{}'.format(el.movie)
            else:
                for el in constant[1].career['actor']:
                    res += '\n{}'.format(el.movie)
        elif constant[2] + 10 < len(x):
            for el in constant[1].career['actor'][constant[2]:constant[2] + 10]:
                res += '\n{}'.format(el.movie)
        else:
            for el in constant[1].career['actor'][constant[2]:len(x)]:
                res += '\n{}'.format(el.movie)
        if mes == 'вернуться к началу':
            res = 'Хорошо, вернёмся'
            update.message.reply_text(res, reply_markup=markup_main_keyboard)
            constant = None
        else:
            if len(constant) == 2:
                res = 'Вот фильмография:' + res
                if len(x) > 10:
                    update.message.reply_text(res, reply_markup=markup_pages)
                    constant = constant + [10]
                else:
                    update.message.reply_text(res, reply_markup=markup_main_keyboard)
                    constant = None
            elif constant[2] + 10 < len(x):
                update.message.reply_text(res, reply_markup=markup_pages)
                constant = constant[0:2] + [constant[2] + 10]
            else:
                res += '\n\nФильмография кончилась.'
                update.message.reply_text(res, reply_markup=markup_main_keyboard)
                constant = None


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
