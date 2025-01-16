# Руководство по запуску проекта

Этот проект представляет собой распределённую систему, включающую несколько микросервисов, таких как **ordex** и **sentinel**, а также инфраструктурные компоненты: PostgreSQL, Redis и Kafka. Ниже описаны шаги для настройки и запуска проекта.

---

## Предварительные требования

Перед началом работы убедитесь, что на вашем компьютере установлены следующие компоненты:

1. **Docker**: версия 26.0.0.
2. Опционально: **git** для клонирования репозитория.

---

## Шаги по настройке и запуску

### 1. Клонирование репозитория

Сначала клонируйте репозиторий проекта на ваш локальный компьютер:

```bash
git clone https://github.com/Kentemie/Nimbus.git
```

### 2. Запуск инфраструктуры

Для работы микросервисов потребуется настроенная инфраструктура, включающая PostgreSQL, Redis и Kafka. Для её запуска выполните следующую команду:

```bash
docker-compose -f docker-compose.infra.yml up -d --build
```

### 3. Запуск микросервисов

После запуска инфраструктуры необходимо запустить микросервисы **ordex** и **sentinel**. Сделайте это, выполнив команды поочерёдно:

#### Запуск сервиса **ordex**:

```bash
docker-compose -f microservices/ordex/docker-compose.ordex.yml up -d --build
```

#### Запуск сервиса **sentinel**:

```bash
docker-compose -f microservices/sentinel/docker-compose.sentinel.yml up -d --build
```

### 4. Применение миграций базы данных

После запуска контейнеров выполните миграции для настройки схемы базы данных PostgreSQL:

```bash
docker exec -it nimbus-ordex alembic upgrade head
```

### 5. Проверка документации

Перейдите в браузере по адресу:

```
http://localhost:8000/docs
```

Вы сможете увидеть автоматически сгенерированную документацию API.

---

## Структура проекта

### Основные сервисы:

1. **ordex**:
   - Отвечает за управление пользователями, ролями, заказами и продуктами.
   - Поддерживает работу с Kafka для публикации событий.

2. **sentinel**:
   - Мок-сервис, симулирующий обработку событий из Kafka.

### Инфраструктура:

- **PostgreSQL**: Хранение данных микросервисов.
- **Redis**: Используется как кэш.
- **Kafka**: Управляет очередями сообщений.

---

## Переменные окружения

Переменные окружения для всех сервисов определены в файлах `.env`. Пример содержимого:

```env
# PostgreSQL
POSTGRES_USER=nimbus_user
POSTGRES_PASSWORD=V4gQp!7xJf9ZLb
POSTGRES_DB=nimbusdb

# Kafka
KAFKA_BROKER_ID=1
KAFKA_CFG_NODE_ID=1
KAFKA_CFG_PROCESS_ROLES=broker,controller
KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=1@localhost:9093
KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093,EXTERNAL://:9094
KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092,EXTERNAL://kafka:9094
```

---

## Команды для остановки

Чтобы остановить контейнеры содержащие инфраструктурные компоненты, выполните следующую команду:

```bash
docker-compose -f docker-compose.infra.yml down
```

Для остановки отдельных микросервисов:

```bash
docker-compose -f microservices/ordex/docker-compose.ordex.yml down
docker-compose -f microservices/sentinel/docker-compose.sentinel.yml down
```

---

## Дополнительная информация

1. **Kafka**:
   - Для управления топиками Kafka используется скрипт `create-topics.sh`. Он автоматически создаёт топик `ordex`, если он ещё не существует.

2. **Логи**:
   - Логи Kafka-consumer хранятся в папке `/app/logs` внутри контейнера `nimbus-event-listener`.
   - Файл логов: `kafka_consumer.log`.

3. **Документация API**:
   - Основной API доступен по адресу `http://localhost:8000/docs`.

---

Если у вас возникли вопросы или проблемы, свяжитесь с разработчиками проекта.
