Experiments with Kafka serialization schemes

# Kafka with AVRO vs., Kafka with Protobuf vs., Kafka with JSON Schema  

Apache Avro was has been the defacto Kafka serialization mechanism for a long time.   Confluent just updated their Kafka streaming platform with additioinal support for serializing data with Protocol buffers (or _protobuf_) and JSON Schema serialization.  The inclusion of Protobuf and JSON Schema applies at producer and consumer libraries, schema registry, Kafka connect, ksqlDB along with Control Center.


## Do I care about serializing structured data?

Why bother with serializing structured data?  Let's start with an example data string ... `cookie,50,null`.  What does this data mean? Is _cookie_ a name, a place or something to eat?  And what about _50_ - is this an age, a temperature or something else?

If you were using a database (such as Postgres or Oracle) to store your data you would create a table definition (with nicely named columns and appropriate data types). The same is true for your streaming platform - you really should pick data format for serializing structured data. Bonus points for and being consistent across your data platform!

Until recently your choices for serializing structured data within Kafka were limited. You had "bad" choices (such as free text or CSV) or the "right" choice of using Apache Avro. Avro is an open source data serialization system which marshals your data (and it's appropriate schema) to a efficient binary format.  One of the core features of Avro is the ability to define a schema for our data. So our data `cookie,50,null` would be associated with a _snack_ Avro schema like this

```
{
  "type": "record",
  "name": "snacks",
  "fields": [
      {"name": "name",  "type": "string" }
    , {"name": "calories", "type": "float" }
    , {"name": "colour", "type": "string", "default": null}
  ]
}
```

Here we can see our data `cookie,50,null` is snack data (the most important type of data). We can see _cookie_ is a _string_ representing the name of the snake. Our schema offers us a lot of flexibility (our schema can evolve over time) plus ensures data integrity (for example, ensuring calories are integers ).  

# AVRO, Protobuf, JSON Schema use with Kafka

This _isn't_ a blog on the "best" serialization strategy. However, let's get familiar with how we can use new choices for serializing structured data

Our initial set of yummy data looks like this

```
{"name": "cookie", "calories": 500, "colour": "brown"}
{"name": "cake", "calories": 260, "colour": "white"}
{"name": "timtam", "calories": 80, "colour": "chocolate"}
```

## AVRO serialization 
Let's remind ourselves how to encode our snacks using AVRO serialization. We'll use the include command line tool `kafka-avro-console-producer` as a Kafka producer which can perform serialization (with a schema provided as a command line parameter)

```
kafka-avro-console-producer  --broker-list localhost:9092 --topic SNACKS_AVRO --property value.schema='
{
  "type": "record",
  "name": "myrecord",
  "fields": [
      {"name": "name",  "type": "string" }
    , {"name": "calories", "type": "float" }
    , {"name": "colour", "type": "string" }
  ]
}' < snacks.txt
```

And to read the data, we can use the `kafka-avro-console-consumer` kafka consumer for de-serializing our AVRO data

```
kafka-avro-console-consumer --bootstrap-server localhost:9092 --topic SNACKS_AVRO --from-beginning 

{"name":"cookie","calories":500.0,"colour":"brown"}
{"name":"cake","calories":260.0,"colour":"white"}
{"name":"timtam","calories":80.0,"colour":"chocolate"}
```

## Protocol Buffers (Protobuf) serialization 

This time we'll use protobuf serialization with the new `kafka-protobuf-console-producer` kafka producer.

```
kafka-protobuf-console-producer --broker-list localhost:9092 --topic SNACKS_PROTO --property value.schema='
message Snack {
    required string name = 1;
    required int64 calories = 2;
    optional string colour = 3;
}' < snacks.txt
```

And to read the data, we can use the `kafka-protobuf-console-consumer` kafka consumer for de-serializing our protobuf data

```
kafka-protobuf-console-consumer --bootstrap-server localhost:9092 --topic SNACKS_PROTO --from-beginning 

{"name":"cookie","calories":"500","colour":"brown"}
{"name":"cake","calories":"260","colour":"white"}
{"name":"timtam","calories":"80","colour":"chocolate"}
```


## JSON Schema serialization 

Finally we'll use JSON Schema serialization with the new `kafka-json-schema-console-producer` kafka producer.

```
kafka-json-schema-console-producer --broker-list localhost:9092 --topic SNACKS_JSONSCHEMA --property value.schema='
{
  "definitions" : {
    "record:myrecord" : {
      "type" : "object",
      "required" : [ "name", "calories" ],
      "additionalProperties" : false,
      "properties" : {
        "name" : {"type" : "string"},
        "calories" : {"type" : "number"},
        "colour" : {"type" : "string"}
      }
    }
  },
  "$ref" : "#/definitions/record:myrecord"
}' < snacks.txt
```

And to read the data, we can use the `kafka-json-schema-console-consumer` kafka consumer for de-serializing our json-schema data

```
kafka-json-schema-console-consumer --bootstrap-server localhost:9092 --topic SNACKS_JSONSCHEMA --from-beginning 

{"name":"cookie","calories":"500","colour":"brown"}
{"name":"cake","calories":"260","colour":"white"}
{"name":"timtam","calories":"80","colour":"chocolate"}
```

# Protobuf with the Confluent Schema Registry

You may have wondered where the schemas actually went?  The Confluent Schema Registry has been diligently storing these schemas (as part of the serialization process when using kafka-blah-console-producer). We can peak at the Protobuf schema with `curl`

```
curl -s -X GET http://localhost:8081/subjects/SNACKS_PROTO-value/versions/1 
```

Which responds

```
{
  "subject": "SNACKS_PROTO-value",
  "version": 1,
  "id": 6,
  "schemaType": "PROTOBUF",
  "schema": "\nmessage Snack {\n  required string name = 1;\n  required int64 calories = 2;\n  required string colour = 3;\n}\n"
}
```

# Schema Evolution with Protobuf 
- consumer


## Complex
```
kafka-protobuf-console-producer --broker-list localhost:9092 --topic PERSON_PROTO --property value.schema='
message Person {
  required string name = 1;
  required int32 id = 2;
  optional string email = 3;
  optional string twitter = 5;

  enum PhoneType {
    MOBILE = 0;
    HOME = 1;
    WORK = 2;
  }

  message PhoneNumber {
    required string number = 1;
    optional PhoneType type = 2 [default = HOME];
  }

  repeated PhoneNumber phone = 4;
}'

{"name":"bob", "id": 1}
{"name":"alice", "id": 2, "email": "example@example.com"}
{"name":"alice","id":2,"email":"example@example.com","phone":[{"number":"123","type":"HOME"},{"number":"456","type":"HOME"}]}
```

# Application Binding - Protobuf classes with Python
Let us now build an application demonstrating protobuf classes


To regenerate Protobuf classes you must first install the protobuf compiler.  See the protocol buffer docs for instructions on installing and using protoc.
https://developers.google.com/protocol-buffers/docs/pythontutorial



### Setup Python virtual environment 

```
virtualenv myenv
. ./myenv/bin/activate
pip install -r requirements.txt
```

### Python compile schema
```
protoc -I=. --python_out=. ./user.proto
```




## Other Profotbuf tips with protoc

To encode
```
protoc --encode="Foo" ./my.proto < mydata.txt  > mydata.prot
```

To decode
```
protoc --decode="Foo" ./my.proto < mydata.prot
```


```
kafka-protobuf-console-producer --broker-list localhost:9092 --topic mytopic1 --property value.schema='
message Foo { required string f1 = 1; }'
```



# References

- https://www.confluent.io/blog/confluent-platform-now-supports-protobuf-json-schema-custom-formats/
- https://blog.softwaremill.com/the-best-serialization-strategy-for-event-sourcing-9321c299632b


