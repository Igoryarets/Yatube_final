[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)



[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)


## Проект Yatube

Социальная сеть

## Описание

Благодаря этому проекту можно создавать посты, оставлять комментарии под постами и подписываться на понравившихся авторов.

## Технологии

Python, Django, sorl-thumbnail, Bootstrap.

## Запуск проекта в dev-режиме

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Igoryarets/hw05_final.git
```

Установите и активируйте виртуальное окружение:

```
Для пользователей Windows:
python -m venv venv
source venv/Scripts/activate
```

Обновите менеджер пакетов pip:

```
python -m pip install --upgrade pip
```

Перейдите в каталог с файлом manage.py выполните команды: Выполнить миграции:

```
python manage.py migrate
```

Создайте супер-пользователя:

```
python manage.py createsuperuser
```

Соберите статику:

```
python manage.py collectstatic
```

Запуск проекта в режиме dev сервера:

```
python manage.py runserver
```

## Подробнее о проекте:

# С помощью sorl-thumbnail выведены иллюстрации к постам:

    в шаблон главной страницы,
    в шаблон профайла автора,
    в шаблон страницы группы,
    на отдельную страницу поста.

# Создана система комментариев:
  Написана система комментирования записей. На странице поста под текстом записи выводится форма для отправки комментария, 
  а ниже — список комментариев. Комментировать могут только авторизованные пользователи. 

# Кеширование главной страницы:
  Список постов на главной странице сайта хранится в кэше и обновляется раз в 20 секунд.

# Система подписок:

  Создана система подписок на авторов. Авторизованный пользователь может подписываться на других 
  пользователей и удалять их из подписок. Новая запись пользователя появляется в ленте тех, кто 
  на него подписан и не появляется в ленте тех, кто не подписан.

# Регистрация и авторизация:

  Подключена система регистрации и авторизации

# Тесты:
  
  На все приложения проекта написаны тесты с помощью библиотеки Unittest
