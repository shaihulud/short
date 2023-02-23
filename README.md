# Table of Contents
- [ Short Project Description English ](#descen)
- [ Русское описание проекта Short ](#descru)

<a name="descen"></a>
# Short Project Description

## Technical Requirements

The goal is to write a simple short link service.

The short links service allows you to make short URLs from long links to the original resource. This short URLs will redirect user to the original resource when clicked.

Analog - bit.ly

In this task, you do not need to write all possible functions (authorization, browser user interface, etc.), but focus on the most important.

Functional requirements:
- POST request to \<hostname>/urls with the original link, generates a new short URL and returns it in the format \<hostname>/urls/\<short code>, where \<short code> is the short unique "code" of the link
- GET request to \<hostname>/urls/\<short code> redirects the user to the original link
- GET request to \<hostname>/urls/\<short code>/stats returns the number of clicks on the link for the last 24 hours
- PUT request to \<hostname>/urls/\<short code> with new link updates existing short link
- DELETE request to \<hostname>/urls/\<short code> removes the short link

## Project Launch
    docker-compose-up

The project starts on port 8000 in a Docker image with Redis and PostgreSQL.
An interface for convenient access to the project API after the start is available at http://127.0.0.1:8000/docs

Every API endpoint has a description and is available without authorization.

## Run tests
    docker-compose run app tests

Runs code checkers: isort, black, pylint, mypy.
Next, it updates the database structure and runs pytest.

## Structure
At the root of the short project are the following directories:
- app - contains the Python code for the short link service
- migrations - contains migrations for the Postgres database with the necessary tables, indexes and system files.
- tests - contains not as many tests as would be enough :(
- system files for starting a project through docker, linter settings and dependency lists.

The app directory contains the following project directories and files:
- server.py - starting point, main project file. Contains settings for logging, managing exceptions and converting them into a form that the frontend can easily parse and display. As well as scripts that once per hour clear old data from tables with URLs and statistics. According to the requirements I only show statistics for the last 24 hours, so I decided not to keep it longer. Naturally, if there is space and other technical requirements, it will look different.
- logging.py - file with logging settings
- exceptions.py - a file with exception settings that the user should not see, ex. a 500 error. When adding an exception to the list, it will be caught, processed and sent to the frontend in standard JSON error format.
- db.py - base class for inheritance of SQLAlchemy models and their standardization
- utils.py - a couple of small functions used in the project
- config.py - application settings. If you put the .env file in the root of the project, then the settings defined in it will overwrite those from the config.
- api directory - contains "probes" - small API endpoints that show the current state of the service and its performance.
- apps/urls/models.py and apps/urls/schemas.py - contains SQLAlchemy models for the database and Pydantic models for displaying and verifying user input
- and finally =) apps/urls/api/urls.py - a list of methods that, according to the requirements, I had to implement.

<a name="descru"></a>
# Русское описание проекта Short

## ТЗ

Цель -- написать простой сервис коротких ссылок.

Сервис коротких ссылок позволяет из длинных URL на оригинальный ресурс
сделать короткие URL, которые при переходе перенаправляют на оригинальный.
Аналог - bit.ly

В этом задании не нужно писать все возможные функции (авторизацию, браузерный
пользовательский интерфейс, итд), а сосредоточиться на самом главном. 

Функциональные требования:
- POST запрос на \<hostname>/urls с оригинальной ссылкой, генерирует новый короткий URL, 
  и возвращает его в формате \<hostname>/urls/\<short code>, где \<short code> это короткий
  уникальный "код" ссылки
- GET запрос на \<hostname>/urls/\<short code> перенаправляет пользователя на оригинальную
  ссылку
- GET запрос на \<hostname>/urls/\<short code>/stats возвращает количество переходов по
  ссылке за последние 24 часа
- PUT запрос на \<hostname>/urls/\<short code> с новой ссылкой обновляет существующую
  короткую ссылку
- DELETE запрос на \<hostname>/urls/\<short code> удаляет короткую ссылку

Нефункциональные требования:
- Желательно выложить код в git репозиторий (github, gitlab, bitbucket, или любой другой
  по выбору).
- Язык программирования лучше всего -- Python, но любой другой тоже подойдет, если на нем есть
  хорошие рабочие навыки и это сэкономит время.
- Лучше всего писать меньше кода, но качественно. Так, чтобы это демонстрировало реальные
  "боевые" навыки.

## Запуск проекта
    docker-compose up

Проект стартует на порту 8000 в Docker образе с Redis и PostgreSQL.
Интерфейс для удобного доступа к API проекта после старта доступен по адресу http://127.0.0.1:8000/docs

Каждая ручка имеет описание и доступна без авторизации.

## Запуск тестов
    docker-compose run app tests

Запускает чекеры кода: isort, black, pylint, mypy.
Далее обновляет структуру БД и запускает тесты pytest.

## Структура
В корне проекта short лежат следующие директории:
- app, содержащая код на Python сервиса коротких ссылок
- migrations, содержащая миграции для БД Postgres с необходимыми таблицами, индексами и системными файлами.
- tests, содержащая не столь большое количество тестов, как бы того хотелось :(
- системные файлы для старта проекта через докер, настройки линтеров и списки зависимостей. 

В директории app содержатся следующие директории и файлы проекта:
- server.py - стартовая точка, главный файл проекта. Содержит настройки логирования, управления исключениями и преобразования их в вид, который фронтэнд сможет легко распарсить и отобразить. А так же скрипты, которые раз в час очищают старые данные из таблиц с УРЛами и статистики. Поскольку по ТЗ я показываю статистику только за последние 24 часа, я решил не хранить её дольше. Естественно, при наличии места и отличного ТЗ это будет выглядеть иначе.
- logging.py - файл с настройками логирования
- exceptions.py - файл с настройками исключений, которые пользователь видеть не должен, как 500 ошибку на весь экран. При добавлении исключения в список, оно будет перехвачено, обработано и отдано на фронт в виде стандартного JSON.
- db.py - базовый класс для наследования SQLAlchemy моделей и их стандартизации
- utils.py - пара используемых в проекте небольших функций
- config.py - настройки приложения. Если в корень проекта положить файл .env, то определённые в нём настройки перезапишут таковые из конфига.
- директория api - содержит "пробы" - небольшие ручки, которые показывают текущее состояние сервиса, его работоспособность.
- apps/urls/models.py и apps/urls/schemas.py - содержит модели SQLAlchemy для БД, модели Pydantic для отображения и верификации пользовательского ввода
- и, наконец-то =), apps/urls/api/urls.py - список методов, которые по ТЗ я и должен был реализовать.
