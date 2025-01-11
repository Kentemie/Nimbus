#!/bin/bash

echo "Waiting for Kafka to be ready..."
while ! nc -z kafka 9094; do
  sleep 1
done

kafka-topics.sh --create --topic ordex \
  --bootstrap-server kafka:9094 \
  --partitions 3 \
  --replication-factor 1

echo "Topic ordex created."