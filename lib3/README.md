# 📚 Library Management System

Django-приложение для управления сетью библиотек.
Центральный каталог книг + отдельная БД на каждый филиал.

---

## Архитектура

```
default (db_central.sqlite3)   ← Книги, авторы, жанры, филиалы, экземпляры
branch_1 (db_branch_1.sqlite3) ← Читатели и выдачи Филиала №1
branch_2 (db_branch_2.sqlite3) ← Читатели и выдачи Филиала №2
```

**Роутер** (`routers/db_router.py`) автоматически направляет:
- `catalog` → `default`
- `lending` → нужный `branch_*`

---

## Установка

```bash
# 1. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Применить миграции для ВСЕХ БД
python manage.py migrate                     # default
python manage.py migrate --database=branch_1
python manage.py migrate --database=branch_2

# 4. Создать суперпользователя
python manage.py createsuperuser

# 5. Запустить сервер
python manage.py runserver
```

Открыть в браузере: http://127.0.0.1:8000/

---

## Добавить новый филиал

1. В `settings.py` добавь в `DATABASES`:
```python
'branch_3': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': BASE_DIR / 'db_branch_3.sqlite3',
},
```

2. Добавь в `BRANCH_DATABASES`:
```python
3: {'name': 'Филиал №3 — Юг', 'db': 'branch_3'},
```

3. Примени миграции:
```bash
python manage.py migrate --database=branch_3
```

4. Создай запись `Branch` в Django Admin с `db_alias = branch_3`.

---

## REST API

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/books/` | Список книг |
| GET | `/api/books/?search=название` | Поиск |
| GET | `/api/books/available/?branch_id=1` | Доступные в филиале |
| GET | `/api/branches/` | Список филиалов |
| GET | `/api/readers/?branch_id=1` | Читатели филиала |
| GET | `/api/loans/?branch_id=1` | Выдачи филиала |
| POST | `/api/loans/issue/` | Выдать книгу |
| POST | `/api/loans/{id}/return_book/` | Вернуть книгу |

### Пример: выдать книгу через API

```bash
curl -X POST http://127.0.0.1:8000/api/loans/issue/ \
  -H "Content-Type: application/json" \
  -d '{
    "book_copy_id": 1,
    "reader_id": 1,
    "due_days": 14
  }' \
  "?branch_id=1"
```

---

## Структура проекта

```
library_system/
├── manage.py
├── requirements.txt
├── library_project/
│   ├── settings.py       ← Конфиг БД и филиалов
│   └── urls.py           ← Маршруты
├── routers/
│   └── db_router.py      ← Роутер multi-DB
├── catalog/              ← Глобальный каталог (default БД)
│   ├── models.py         ← Book, Author, Genre, Branch, BookCopy
│   ├── views.py          ← Web + API views
│   ├── serializers.py
│   └── admin.py
├── lending/              ← Выдача/возврат (branch БД)
│   ├── models.py         ← Reader, Loan
│   ├── views.py          ← Web + API + переключение филиала
│   ├── serializers.py
│   └── admin.py
└── templates/
    ├── base.html
    ├── catalog/
    │   ├── book_list.html
    │   ├── book_detail.html
    │   └── branch_list.html
    └── lending/
        ├── loan_list.html
        ├── issue_book.html
        ├── return_book.html
        └── reader_list.html
```
