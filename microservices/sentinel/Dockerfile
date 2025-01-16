# Dockerfile
FROM python:3.12-alpine

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Скопируем только requirements.txt (для кеширования слоёв)
COPY requirements.txt /app/requirements.txt

# Установим зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Скопируем весь проект
COPY . /app

# Запускаем моковый event-listener
CMD ["python", "consumer.py"]