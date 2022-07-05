# Yatube
Yatube - социальная сеть для публикации блогов, с возможностью постить как в общую ленту, так и в группы по интересам. Имеет возможность подписываться на интересных авторов.
***
## Стек технологий
Python 3.7+, Django 2.2.6, unittest, pytest
***
## Установка
#### После клонирования репозитория перейдите в каталог hw05_final и создайте виртуальное окружение:
    python3 -m venv venv

#### Активируйте виртуальное окружение:
    . venv/Scripts/activate

#### Установите необходимые зависимости:
    pip install -r requirements.txt

#### Примените миграции:
    python manage.py migrate

#### Соберите статику:
    python manage.py collectstatic

#### Создайте суперпользователя:
    python manage.py createsuperuser
После создания суперпользователя и запуска сервера, вам будет доступна админка (/admin), из которой можно управлять проектом, добавлять и удалять группы, посты, пользователей  и т.д.

#### Запускайте сервер:
    python manage.py runserver
Теперь вы можете создать перый пост на сайте))
***
## Тесты
#### Тесты запускаются командой:
    python manage.py test
#### или командой:
    pytest
