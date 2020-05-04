from keyboards import markup_main_keyboard, markup_back, markup_yesornot, markup_pages
from kinopoisk.movie import Movie
from kinopoisk.person import Person

# Постоянная, которая запоминает выбор пользователя.
# Используется, чтобы не использовать менее подходящие встроенные методы запоминания выбора пользователя
constant = None


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
        # Команда, которая позволяет вернуться к основной клавиатуре в любой момент использования бота.
        update.message.reply_text("Хорошо, вернёмся.", reply_markup=markup_main_keyboard)
        constant = None
    elif constant == 'film_search':
        movie_list = Movie.objects.search(mes)  # Список из всех фильмов результатов поиска, чаще всего имеет длину 11
        length = len(movie_list)  # Чтобы постоянно не пересчитывать длину функции
        if length == 0:
            update.message.reply_text('Извините, фильма с таким названием не найдено. Вернёмся к началу.',
                                      reply_markup=markup_main_keyboard)
            constant = None
        elif length >= 1:
            movie = Movie(id=movie_list[0].id)  # Чтобы вызвать команду в следующей строке, нужно найти фильм по id
            movie.get_content('main_page')  # Обязательная команда, чтобы получить информацию кроме года и названия
            update.message.reply_text(
                'Полное название - {}.\n{}\nСлоган - {}\nГод - {}\nДлительность - {}\nРейтинг фильма - {}'
                '\nХотите увидеть список актёров?'.format(
                    movie.title, movie.plot, movie.tagline,
                    movie.year, movie.runtime, movie.rating), reply_markup=markup_yesornot)
            constant = ['cast', movie.actors]
            # Передаём список, чтобы суметь обратить к списку актёров, если он нам понадобится
    elif constant[0] == 'cast':
        res = ''
        x = constant[1]
        for el in x[:10]:
            res += '\n{}'.format(el)
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
            constant = ['filmography', actor.career['actor']]
    elif constant[0] == 'filmography':
        res = ''
        x = constant[1]
        # Переменные, чтобы не использовать функцию len() много раз
        length_x = len(x)
        length_con = len(constant)
        # Так как у актёра может быть очень много фильмов и
        # их построчный вывод может занять долгое время и несколько страниц,
        # что окажется неудобным для пользователя, мы будем выводить по 10 фильмов за раз
        if length_con == 2:
            # Если мы выводим первую страницу фильмографии, длина константы будет равна двум,
            # так что мы будем выводить первые 10 (или все, если length_x <= 10)
            if length_x > 10:
                for el in x[:10]:
                    res += '\n{}'.format(el.movie)
            else:
                for el in x:
                    res += '\n{}'.format(el.movie)
        elif constant[2] + 10 < length_x:
            # Если невыведенных элементов в списке всё ещё больше 10, мы выводим только следующие 10
            for el in x[constant[2]:constant[2] + 10]:
                res += '\n{}'.format(el.movie)
        else:
            # Если невыведенных элементов в списке осталось 10 или меньше, мы выводим последние элементы
            for el in x[constant[2]:length_x]:
                res += '\n{}'.format(el.movie)
        if length_con == 2:
            # Длина константы равна двум, если мы выводим первую страницу фильмографии.
            # В таком случае мы добавим в начало фразу "Вот фильмография:"
            res = 'Вот фильмография:' + res
            if length_x > 10:
                update.message.reply_text(res, reply_markup=markup_pages)
                constant = constant + [10]
                # Если в списке фильмов больше 10 кинокартин, мы выводим клавиатуру с предложением продолжить вывод
                # и добавляем третий элемент к константе - количество уже выведенных фильмов
            else:
                update.message.reply_text(res + '\n\nФильмография кончилась.', reply_markup=markup_main_keyboard)
                constant = None
                # Если в списке меньше 10 кинокартин, мы выводим основную клавиатуру и меняем константу на None
        elif constant[2] + 10 < length_x:
            update.message.reply_text(res, reply_markup=markup_pages)
            constant = constant[0:2] + [constant[2] + 10]
            # Если невыведенные элементы в списке ещё есть, мы изменяем последний элемент константы
            # и показываем клавиатуру с предложением продолжить вывод
        else:
            res += '\n\nФильмография кончилась.'
            update.message.reply_text(res, reply_markup=markup_main_keyboard)
            constant = None
            # Если невыведенных элементов в списке не осталось, мы выводим основную клавиатуру
            # и меняем константу на None
