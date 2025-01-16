FROM python:3.12-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /ordex

# Устанавливаем переменные окружения для python
ENV PYTHONPATH=/ordex/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Обновляем пакеты и устанавливаем зависимости сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libssl-dev \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Скопируем только requirements.txt (для кеширования слоёв)
COPY requirements.txt /ordex/requirements.txt

# Установим зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Скопируем весь проект
COPY . /ordex

# По умолчанию запускаем FastAPI-приложение через Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]