"""
python manage.py seed_books
python manage.py seed_books --count 200
"""
from django.core.management.base import BaseCommand
from catalog.models import Author, Genre, Book, BookCopy, Branch


GENRES = [
    'Роман', 'Фантастика', 'Детектив', 'История', 'Биография',
    'Поэзия', 'Философия', 'Психология', 'Детская литература', 'Классика',
]

BOOKS_DATA = [
    # (Название, Автор-фамилия, Автор-имя, Год, ISBN, Жанр)
    ('Война и мир',               'Толстой',       'Лев',         1869, '978-5-17-090001-1', 'Роман'),
    ('Преступление и наказание',  'Достоевский',   'Фёдор',       1866, '978-5-17-090002-2', 'Роман'),
    ('Мастер и Маргарита',        'Булгаков',      'Михаил',      1967, '978-5-17-090003-3', 'Роман'),
    ('Евгений Онегин',            'Пушкин',        'Александр',   1833, '978-5-17-090004-4', 'Поэзия'),
    ('Идиот',                     'Достоевский',   'Фёдор',       1869, '978-5-17-090005-5', 'Роман'),
    ('Отцы и дети',               'Тургенев',      'Иван',        1862, '978-5-17-090006-6', 'Роман'),
    ('Мёртвые души',              'Гоголь',        'Николай',     1842, '978-5-17-090007-7', 'Классика'),
    ('Анна Каренина',             'Толстой',       'Лев',         1878, '978-5-17-090008-8', 'Роман'),
    ('Братья Карамазовы',         'Достоевский',   'Фёдор',       1880, '978-5-17-090009-9', 'Роман'),
    ('1984',                      'Оруэлл',        'Джордж',      1949, '978-5-17-090010-0', 'Фантастика'),
    ('Дюна',                      'Херберт',       'Фрэнк',       1965, '978-5-17-090011-1', 'Фантастика'),
    ('Гарри Поттер и философский камень', 'Роулинг', 'Джоан',     1997, '978-5-17-090012-2', 'Детская литература'),
    ('Маленький принц',           'Сент-Экзюпери', 'Антуан',      1943, '978-5-17-090013-3', 'Детская литература'),
    ('Над пропастью во ржи',      'Сэлинджер',     'Джером',      1951, '978-5-17-090014-4', 'Роман'),
    ('Шерлок Холмс',              'Конан Дойл',    'Артур',       1892, '978-5-17-090015-5', 'Детектив'),
    ('Убийство в Восточном экспрессе', 'Кристи',   'Агата',       1934, '978-5-17-090016-6', 'Детектив'),
    ('Три товарища',              'Ремарк',        'Эрих',        1936, '978-5-17-090017-7', 'Роман'),
    ('Граф Монте-Кристо',         'Дюма',          'Александр',   1846, '978-5-17-090018-8', 'Роман'),
    ('Сапиенс',                   'Харари',        'Юваль',       2011, '978-5-17-090019-9', 'История'),
    ('Думай медленно решай быстро', 'Канеман',     'Даниэль',     2011, '978-5-17-090020-0', 'Психология'),
]


class Command(BaseCommand):
    help = 'Массово добавляет книги в каталог'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count', type=int, default=None,
            help='Сколько книг добавить (по умолч. все из списка)'
        )
        parser.add_argument(
            '--with-copies', action='store_true',
            help='Добавить по 1 экземпляру книги в каждый филиал'
        )

    def handle(self, *args, **options):
        # Создаём жанры
        genre_objs = {}
        for g in GENRES:
            obj, _ = Genre.objects.get_or_create(name=g)
            genre_objs[g] = obj
        self.stdout.write('✅ Жанры готовы')

        data = BOOKS_DATA[:options['count']] if options['count'] else BOOKS_DATA

        created_books = 0
        skipped = 0
        for title, last_name, first_name, year, isbn, genre_name in data:
            # Автор
            author, _ = Author.objects.get_or_create(
                last_name=last_name,
                first_name=first_name,
            )
            # Книга (пропускаем если уже есть)
            if Book.objects.filter(isbn=isbn).exists():
                skipped += 1
                continue

            book = Book.objects.create(
                title=title,
                genre=genre_objs[genre_name],
                isbn=isbn,
                year=year,
            )
            book.authors.add(author)
            created_books += 1

            # Экземпляры в каждом филиале
            if options['with_copies']:
                branches = Branch.objects.filter(is_active=True)
                for i, branch in enumerate(branches, start=1):
                    inv = f'{isbn[-4:]}-{branch.db_alias}-{i:03d}'
                    BookCopy.objects.get_or_create(
                        book=book,
                        branch=branch,
                        defaults={'inventory_number': inv, 'status': 'available'}
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Добавлено книг: {created_books} | Уже существовало: {skipped}'
            )
        )
