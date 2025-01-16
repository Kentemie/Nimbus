#!/bin/bash

echo "Waiting for Kafka to be ready..."
while ! nc -z kafka 9094; do
  sleep 1
done

# Проверяем, существует ли топик 'ordex'
if kafka-topics.sh --bootstrap-server kafka:9094 --list | grep -q "^ordex$"; then
  echo "Topic 'ordex' already exists. Skipping creation."
else
  kafka-topics.sh --create --topic ordex \
    --bootstrap-server kafka:9094 \
    --partitions 3 \
    --replication-factor 1
  echo "Topic 'ordex' created."
fi
