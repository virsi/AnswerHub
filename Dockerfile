# Используем официальный образ Python
FROM python:3.13-slim

# Устанавливаем необходимые пакеты
RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект (кроме entrypoint.sh)
COPY . .

# Создаем и настраиваем entrypoint скрипт
RUN echo '#!/bin/bash' > /app/entrypoint.sh && \
    echo 'set -e' >> /app/entrypoint.sh && \
    echo 'python manage.py migrate' >> /app/entrypoint.sh && \
    echo 'python manage.py collectstatic --noinput' >> /app/entrypoint.sh && \
    echo 'python manage.py runserver 0.0.0.0:8000' >> /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Открываем порт
EXPOSE 8000

# Запускаем через entrypoint
CMD ["/bin/bash", "/app/entrypoint.sh"]
