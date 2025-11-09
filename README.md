# AnswerHub

AnswerHub — это веб-платформа вопросов и ответов, построенная на Django. Пользователи могут задавать вопросы, отвечать на них, использовать теги для категоризации и искать по существующему контенту.

## Требования

- Python 3.10 или выше
- PostgreSQL 14 или выше (если запускаете без Docker)
- Docker и Docker Compose (для запуска в контейнерах)

## Быстрый старт с Docker

1. Клонируйте репозиторий:
```bash
git clone https://github.com/virsi/AnswerHub.git
cd AnswerHub
```

2. Создайте файл `.env` из примера:
```bash
cp .env.example .env
```

3. Отредактируйте `.env`, установив безопасный `SECRET_KEY` и желаемые параметры PostgreSQL:
```ini
SECRET_KEY=your-secure-secret-key-here
POSTGRES_DB=answerhub
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

4. Запустите проект через Docker Compose:
```bash
docker-compose up -d
```

5. Создайте суперпользователя:
```bash
docker-compose exec web python manage.py createsuperuser
```

Теперь приложение доступно по адресу: http://localhost:8000

## Локальная установка (без Docker)

1. Клонируйте репозиторий:
```bash
git clone https://github.com/virsi/AnswerHub.git
cd AnswerHub
```

2. Создайте и активируйте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/MacOS
# или
venv\\Scripts\\activate  # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` из примера и настройте его:
```bash
cp .env.example .env
# Отредактируйте .env, указав корректные параметры подключения к вашей PostgreSQL
```

5. Примените миграции:
```bash
python manage.py migrate
```

6. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

7. Соберите статические файлы:
```bash
python manage.py collectstatic
```

8. Запустите сервер разработки:
```bash
python manage.py runserver
```

Приложение будет доступно по адресу: http://localhost:8000

## Миграция с SQLite на PostgreSQL

Если у вас есть существующие данные в SQLite, вы можете перенести их в PostgreSQL:

1. Создайте дамп данных из SQLite:
```bash
python manage.py dumpdata --natural-foreign --natural-primary --exclude contenttypes --exclude auth.permission --indent 2 > data.json --settings=AnswerHub.settings_sqlite
```

2. Убедитесь, что PostgreSQL настроен и миграции применены:
```bash
python manage.py migrate  # или docker-compose exec web python manage.py migrate
```

3. Загрузите данные в PostgreSQL:
```bash
python manage.py loaddata data.json  # или docker-compose exec web python manage.py loaddata data.json
```

## Структура проекта

- `AnswerHub/` - основная директория проекта с настройками
- `questions/` - приложение для работы с вопросами
- `answers/` - приложение для работы с ответами
- `users/` - пользовательское приложение
- `tags/` - приложение для работы с тегами
- `static/` - статические файлы (CSS, JavaScript, изображения)
- `templates/` - HTML шаблоны
- `uploads/` - загружаемые пользователями файлы

## Разработка

1. Создайте ветку для новой функциональности:
```bash
git checkout -b feature/your-feature-name
```

2. Внесите изменения и создайте коммит:
```bash
git add .
git commit -m "Добавлена новая функциональность"
```

3. Отправьте изменения в репозиторий:
```bash
git push origin feature/your-feature-name
```

## Тестирование

Запуск тестов:
```bash
python manage.py test

## Наполнение тестовыми данными

В проект добавлена management command `fill_db` для заполнения БД большим количеством тестовых записей.

Пример использования:

```bash
python manage.py fill_db 100
```

Аргумент `ratio` задаёт базовый коэффициент заполнения:
- пользователей — ratio
- вопросов — ratio * 10
- ответов — ratio * 100
- тегов — ratio
- оценок (вопросы + ответы) — ratio * 200

ВНИМАНИЕ: при больших значениях команда создаёт большое количество записей и может занять много времени и место на диске. Рекомендуется запускать сначала с небольшим ratio (например, 1 или 5) и убедиться, что всё работает корректно.
```

## Дополнительно

### Полезные команды Docker

- Просмотр логов: `docker-compose logs -f`
- Перезапуск сервисов: `docker-compose restart`
- Остановка: `docker-compose down`
- Пересборка: `docker-compose up -d --build`

### Работа с базой данных

- Создание новых миграций: `python manage.py makemigrations`
- Просмотр статуса миграций: `python manage.py showmigrations`
- Доступ к PostgreSQL в контейнере: `docker-compose exec db psql -U postgres`

## Возможные проблемы

1. **Ошибка подключения к базе данных**
   - Убедитесь, что PostgreSQL запущен
   - Проверьте параметры подключения в `.env`
   - При использовании Docker проверьте, что контейнер `db` работает

2. **Статические файлы не отображаются**
   - Выполните `python manage.py collectstatic`
   - Проверьте настройки `STATIC_URL` и `STATIC_ROOT` в `settings.py`

3. **Ошибки при миграции данных**
   - Убедитесь, что все зависимости установлены
   - Проверьте совместимость версий данных
   - При необходимости выполните миграцию поэтапно

## Лицензия

[MIT License](LICENSE)

## Автор

[virsi](https://github.com/virsi)
