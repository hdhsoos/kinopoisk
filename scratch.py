from kinopoisk.movie import Movie
from kinopoisk.person import Person

#movie_list = Movie.objects.search('Redacted')
movie_list = Movie.objects.search('Без цензуры')
print(len(movie_list))
print(movie_list[0].title)
print(movie_list[0].id)
print(movie_list[0].trailers)