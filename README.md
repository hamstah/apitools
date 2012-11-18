Utilities to make defining apis easier

# Tools

## datagenerator 

Class to generate random values given a json-schema.
Doesn't support all json-schema monstruousities, only a subset I find useful.
See TODO.md for what is likely to be implemented next.

## urlsgenerator

Class to generate links defined in the links section of a json-schema.

## invaliddatagenerator

Class to generate invalid data for a given schema

## modelgenerator

Base class to generate models from a schema

## flasksqlalchemymodelgenerator

Generate SQLAlchemy models to be used with flask-sqlalchemy from a schema

## resourceserver

Class to implement the REST api of resources defined in a schema.
Supports creation, update, retrieval, deletion, listing of instances and schema

### Usage

Run the server using
```
$ python resourceserver.py [jsonfile1, jsonfile2, ...]
```

### Example using data/schemas/message.json

```
$ python resourceserver.py data/schemas/message.json
Added message
 * Running on http://0.0.0.0:5000/
```

#### Create a new message

```
$ curl -i -X POST    http://0.0.0.0:5000/messages -d "recipient=07771818335&text=nice message"
HTTP/1.0 201 CREATED
Content-Type: application/json
Content-Length: 13
Location: http://0.0.0.0:5000/messages/2
Server: Werkzeug/0.8.3 Python/2.7.3
Date: Sun, 18 Nov 2012 19:28:56 GMT

{
  "id": 2
}
```

#### List messages

```
$ curl -i -X GET     http://0.0.0.0:5000/messages
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 126
Server: Werkzeug/0.8.3 Python/2.7.3
Date: Sun, 18 Nov 2012 19:32:09 GMT

[
  {"text": "I </3 ninjas", "recipient": "07771818337", "id": 1},
  {"text": "nice message", "recipient": "07771818335", "id": 2}
]
```

#### Retrieve a message

```
$ curl -i -X GET     http://0.0.0.0:5000/messages/2
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 71
Server: Werkzeug/0.8.3 Python/2.7.3
Date: Sun, 18 Nov 2012 19:35:42 GMT

{
  "text": "nice message",
  "recipient": "07771818335",
  "id": 2
}
```

#### Get the json-schema of a message

```
$ curl -i -X OPTIONS http://0.0.0.0:5000/messages/2
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 590
Server: Werkzeug/0.8.3 Python/2.7.3
Date: Sun, 18 Nov 2012 19:37:06 GMT

{
  "description": "Simple message structure",
  "type": "object",
  "properties": {
    "text": {
      "required": true, 
      "type": "string", 
      "maxLength": 140
    }, 
    "recipient": {
      "pattern": "0[0-9]{10}", 
      "required": true,
      "type": "string"
    },
    "id": {
      "minimum": 0,
      "type": "integer"
    }
  },
  "links": [
    {
      "href": "/messages",
      "rel": "root"
    },
    {
      "href": "{id}",
      "rel": "self"
    },
    {
      "rel": "instances"
    },
    {
      "rel": "create"
    }
  ],
  "name": "message"
}
```

#### Update a message

Supports partial updates

```
$ curl -i -X PUT     http://0.0.0.0:5000/messages/2 -d 'recipient=07771818336'
HTTP/1.0 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 0
Server: Werkzeug/0.8.3 Python/2.7.3
Date: Sun, 18 Nov 2012 19:38:02 GMT
```

#### Delete a message

```
$ curl -i -X DELETE  http://0.0.0.0:5000/messages/2
HTTP/1.0 204 NO CONTENT
Content-Type: text/html; charset=utf-8
Content-Length: 0
Server: Werkzeug/0.8.3 Python/2.7.3
Date: Sun, 18 Nov 2012 19:38:38 GMT
```

### Errors examples

#### Trying to set an implicit key

The message.json doesn't define an explicit primary key, but defines `id` as the key in the `rel=self` link.
Each message then gets an additional `id` key managed by the server.
Trying to set or update the `id` results in errors

```
$ curl -i -X POST    http://0.0.0.0:5000/messages   -d "recipient=07771818335&text=nice message&id=7"
$ curl -i -X PUT     http://0.0.0.0:5000/messages/1 -d "recipient=07771818335&text=nice message&id=3"
HTTP/1.0 400 BAD REQUEST
Content-Type: application/json
Content-Length: 43
Server: Werkzeug/0.8.3 Python/2.7.3
Date: Sun, 18 Nov 2012 19:43:48 GMT

{
  "error": "id is read only in message"
}
```
#### Trying to create or update unknown properties

```
$ curl -i -X POST    http://0.0.0.0:5000/messages   -d "recipient=07771818335&tet=nice message&haxxy=foo"
$ curl -i -X PUT     http://0.0.0.0:5000/messages/1 -d "haxxy=foo"
HTTP/1.0 400 BAD REQUEST
Content-Type: application/json
Content-Length: 57
Server: Werkzeug/0.8.3 Python/2.7.3
Date: Sun, 18 Nov 2012 19:56:19 GMT

{
  "error": "message does not have a 'haxxy' property"
}
```

#### Trying to create or update properties with values not respecting constraints

```
$ curl -i -X PUT     http://0.0.0.0:5000/messages/1 -d "recipient=0notanumber&text=nice message"
$ curl -i -X POST    http://0.0.0.0:5000/messages   -d "recipient=0notanumber"
HTTP/1.0 400 BAD REQUEST
Content-Type: application/json
Content-Length: 86
Server: Werkzeug/0.8.3 Python/2.7.3
Date: Sun, 18 Nov 2012 20:03:34 GMT

{
  "error": "'0notanumber' is an invalid recipient value: must match u'0[0-9]{10}'"
}
```

#### Trying to create a message without all the required properties

```
$ curl -i -X POST    http://0.0.0.0:5000/messages -d "recipient=012345678901"HTTP/1.0 400 BAD REQUEST
Content-Type: application/json
Content-Length: 44
Server: Werkzeug/0.8.3 Python/2.7.3
Date: Sun, 18 Nov 2012 20:06:00 GMT

{
  "error": "text is required in message"
}
```

# Dependencies

## Required
run init.sh in dependencies

## Optional

Needed for flasksqlalchemymodelgenerator and resourceserver only

flask-sqlalchemy is required, use flasksqlalchemy-requirements.txt with virtualenv

