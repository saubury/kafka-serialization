#!/usr/bin/env python

# For a complete example; see https://github.com/confluentinc/confluent-kafka-python/blob/master/examples/protobuf_producer.py
from uuid import uuid4

# Protobuf generated class; resides at ./person_pb2.py
# Create it by running
# protoc -I=. --python_out=. ./person.proto

import person_pb2
from confluent_kafka import SerializingProducer
from confluent_kafka.serialization import StringSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer

topic = 'DEMO_PERSON_PROTO'
schema_registry_client = SchemaRegistryClient({'url': 'http://localhost:8081'})
protobuf_serializer = ProtobufSerializer(person_pb2.Person, schema_registry_client)

producer_conf = {'bootstrap.servers':  'localhost:9092', 'key.serializer': StringSerializer('utf_8'), 'value.serializer': protobuf_serializer}
 
producer = SerializingProducer(producer_conf)

producer.poll(0.0)
# user = user_pb2.User(name='alice', favorite_color='blue', favorite_number=27)
phone = person_pb2.Person.PhoneNumber(number='555-12345')
person = person_pb2.Person(name='alice', id=2, email='example@example.com', phone=[phone])

producer.produce(topic=topic, key=str(uuid4()), value=person)
producer.flush()


# message Person {
#   required string name = 1;
#   required int32 id = 2;
#   optional string email = 3;
#   repeated .Person.PhoneNumber phone = 4;

#   message PhoneNumber {
#     required string number = 1;
#     optional .Person.PhoneType type = 2 [default = HOME];
#   }
#   enum PhoneType {
#     MOBILE = 0;
#     HOME = 1;
#     WORK = 2;
#   }
# }
