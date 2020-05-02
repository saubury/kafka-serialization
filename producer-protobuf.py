#!/usr/bin/env python
# For a complete example; see https://github.com/confluentinc/confluent-kafka-python/blob/master/examples/protobuf_producer.py

from uuid import uuid4

# Protobuf generated class; resides at ./meal_pb2.py
# Create it by running
# protoc -I=. --python_out=. ./meal.proto

import meal_pb2
from confluent_kafka import SerializingProducer
from confluent_kafka.serialization import StringSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer

topic = 'DEMO_MEAL_PROTO'
schema_registry_client = SchemaRegistryClient({'url': 'http://localhost:8081'})
protobuf_serializer = ProtobufSerializer(meal_pb2.Meal, schema_registry_client)

producer_conf = {'bootstrap.servers':  'localhost:9092', 'key.serializer': StringSerializer('utf_8'), 'value.serializer': protobuf_serializer}
 
producer = SerializingProducer(producer_conf)

producer.poll(0.0)

mybeer = meal_pb2.Meal.DrinkItems(drink_name="beer")
mywine = meal_pb2.Meal.DrinkItems(drink_name="wine")

meal = meal_pb2.Meal(name='pizza', drink=[mybeer,mywine])

producer.produce(topic=topic, key=str(uuid4()), value=meal)
producer.flush()

