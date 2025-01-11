#!/bin/bash

# Запускаем основной скрипт Kafka от bitnami в фоне
/opt/bitnami/scripts/kafka/entrypoint.sh /run.sh &

# Ждём, пока Kafka действительно поднимется
/usr/local/bin/create-topics.sh

# Не даём контейнеру завершиться
wait -n
