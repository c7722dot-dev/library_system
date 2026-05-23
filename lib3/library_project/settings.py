"""
Library Management System Settings
Центральная БД + отдельные БД для каждого филиала
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-change-this-in-production-!!!!'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'catalog',
    'lending',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'library_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'library_project.wsgi.application'

# =============================================================
# MULTI-DATABASE SETUP
# default   = центральная БД (филиалы, книги-каталог глобально)
# branch_1  = БД филиала №1
# branch_2  = БД филиала №2
# Добавляй новые филиалы по этому шаблону
# =============================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_central.sqlite3',
    },
    'branch_1': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_branch_1.sqlite3',
    },
    'branch_2': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_branch_2.sqlite3',
    },
}

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DATABASE_ROUTERS = ['routers.db_router.BranchRouter']

# Технический маппинг: id филиала -> alias БД
# Названия филиалов хранятся в БД (модель Branch), не здесь.
# Чтобы добавить новый филиал:
#   1. Добавь запись в DATABASES ниже
#   2. Добавь запись здесь
#   3. Запусти: python manage.py migrate --database=branch_3
#   4. Создай филиал через /admin/ или через страницу /branches/manage/
BRANCH_DATABASES = {
    1: {'db': 'branch_1'},
    2: {'db': 'branch_2'},
    3: {'db': 'branch_3'},
    4: {'db': 'branch_4'},
    5: {'db': 'branch_5'},
    6: {'db': 'branch_6'},
    7: {'db': 'branch_7'},
    8: {'db': 'branch_8'},
    9: {'db': 'branch_9'},
    10: {'db': 'branch_10'},
    11: {'db': 'branch_11'},
    12: {'db': 'branch_12'},
    13: {'db': 'branch_13'},
    14: {'db': 'branch_14'},
    15: {'db': 'branch_15'},
    16: {'db': 'branch_16'},
    17: {'db': 'branch_17'},
    18: {'db': 'branch_18'},
    19: {'db': 'branch_19'},
    20: {'db': 'branch_20'},
    21: {'db': 'branch_21'},
    22: {'db': 'branch_22'},
    23: {'db': 'branch_23'},
    24: {'db': 'branch_24'},
    25: {'db': 'branch_25'},
    26: {'db': 'branch_26'},
    27: {'db': 'branch_27'},
    28: {'db': 'branch_28'},
    29: {'db': 'branch_29'},
    30: {'db': 'branch_30'},
    31: {'db': 'branch_31'},
    32: {'db': 'branch_32'},
    33: {'db': 'branch_33'},
    34: {'db': 'branch_34'},
    35: {'db': 'branch_35'},
    36: {'db': 'branch_36'},
    37: {'db': 'branch_37'},
    38: {'db': 'branch_38'},
    39: {'db': 'branch_39'},
    40: {'db': 'branch_40'},
    41: {'db': 'branch_41'},
    42: {'db': 'branch_42'},
    43: {'db': 'branch_43'},
    44: {'db': 'branch_44'},
    45: {'db': 'branch_45'},
    46: {'db': 'branch_46'},
    47: {'db': 'branch_47'},
    48: {'db': 'branch_48'},
    49: {'db': 'branch_49'},
    50: {'db': 'branch_50'},
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'hy'
TIME_ZONE = 'Asia/Yerevan'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
