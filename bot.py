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
    if mes == 'найти фильм по названию':
        update.message.reply_text('Введите название фильма на русском или английском языке.', reply_markup=markup_back)
        constant = 'film_search'
    elif mes == 'найти информацию об актёре':
        update.message.reply_text('Введите имя знаменитости на русском или английском языке.', reply_markup=markup_back)
        constant = 'actor_search'
    elif mes == 'вернуться к началу':
        update.message.reply_text("Хорошо, вернёмся.", reply_markup=markup_main_keyboard)
        constant = None
    if constant == 'film_search':
        constant = None
        movie_list = Movie.objects.search(mes)
        print('работает?')
        lenght = len(movie_list)  # Чтобы постоянно не пересчитывать длину функции
        if lenght == 0:
            update.message.reply_text('Извините, фильма с таким названием не найдено. Вернёмся к началу.',
                                      reply_markup=markup_main_keyboard)
        elif lenght == 1:
            update.message.reply_text(
                'Найден один фильм. Полное название - {}.\n{}\nСлоган - {}\nГод - {}\nДлительность - {}\nРейтинг фильма - {}'.format(
                    movie_list[0].title, movie_list[0].plot, movie_list[0].tagline,
                    movie_list[0].year, movie_list[0].runtime, movie_list[0].rating))
        elif lenght > 1:
            comment = pymorphy2.parse('фильм')[0]
            if lenght >= 6:
                res = 'Найдено {} {}. Вот первые 5 из них:\n'.format(lenght,
                                                                     comment.make_agree_with_number(
                                                                         lenght).word)
                for i in range(6):
                    res += movie_list[i].title + '\n'
            else:
                res = 'Найдено {} {}. Вот они:\n'.format(lenght,
                                                         comment.make_agree_with_number(
                                                             lenght).word)
                for i in range(movie_list):
                    res += movie_list[i].title + '\n'
            res += 'Выберите один с помощью клавиатуры.'
            print('почмеу не рабтате')
            if lenght >= 5:
                update.message.reply_text(res, reply_markup=markup_morethanfive)
            return
    elif constant == 'actor_search':
        actor_list = Person.objects.search(mes)
        lenght = len(actor_list)
        if lenght == 0:
            update.message.reply_text('Извините, актёра с таким именем найти не удалось. Вернёмся к началу.',
                                      reply_markup=markup_main_keyboard)
        elif lenght == 1:
            update.message.reply_text(
                'Полное имя актёра - {}. '.format(
                    actor_list[0].name))
        return


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
