FROM python:3.12-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Обновляем пакеты и устанавливаем зависимости сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libssl-dev \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Скопируем только requirements.txt (для кеширования слоёв)
COPY requirements.txt /app/requirements.txt

# Установим зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Скопируем весь проект
COPY . /app

# Запускаем моковый event-listener
CMD ["python", "consumer.py"]