Utilities to make defining apis easier

# Tools

## datagenerator 

Class to generate random values given a json-schema.  
Doesn't support all json-schema monstruousities, only a subset I find useful.  
See TODO.md for what is likely to be implemented next.  

---

## urlsgenerator

Class to generate links defined in the links section of a json-schema.

---

## invaliddatagenerator

Class to generate invalid data for a given schema

---

## modelgenerator

Base class to generate models from a schema

---

## flasksqlalchemymodelgenerator

Generate SQLAlchemy models to be used with flask-sqlalchemy from a schema

---

## backbonemodelgenerator

Generate models and collections for Backbone.js from a schema.  
The models generated use the primary key defined in the `rel=self` link or `id` by default.  
To be able to use collections, make sure your schema has a `rel=instances` link or `fetch` won't work.  

### Usage

```
$ python backbonemodelgenerator.py -h
Usage: backbonemodelgenerator.py jsonfile1 [jsonfile2]...

Options:
  -h, --help            show this help message and exit
  -t OUTPUT_TYPE, --type=OUTPUT_TYPE
                        Output type (js|wrapped|html)
```

### Output types

#### js

Outputs only the js code for the models/collections

```
$ python backbonemodelgenerator.py -t js data/schemas/message.json

App.Models.Message = Backbone.Model.extend({
    urlRoot: '/messages',
    idAttribute: 'id'
});

App.Collections.Messages = Backbone.Collection.extend({
    model : App.Models.Message,
    url : "/messages"
});
```

#### wrapped

Wraps the js code into `$(document).ready()`

```
$ python backbonemodelgenerator.py -t wrapped data/schemas/message.json

$(document).ready(function() {

    window.App = { Models : {}, Collections : {} };
    
    App.Models.Message = Backbone.Model.extend({
        urlRoot: '/messages',
        idAttribute: 'id'
    });
    
    App.Collections.Messages = Backbone.Collection.extend({
        model : App.Models.Message,
        url : "/messages"
    });

});
```

#### html

Same as wrapped but generate a whole html page including jQuery, Backbone and Underscore to easily test.

### Example usage

#### Setup

You can use it with resource server for example
```
$ mkdir static
$ python backbonemodelgenerator.py -t html data/schemas/message.json > static/index.html
$ python resourceserver.py data/schemas/message.json
Added message
 * Running on http://0.0.0.0:5000/
```

Now open your browser at http://0.0.0.0:5000/static/index.html
Open your js console to start playing

#### Create a collection and fetch them

```
var col = new App.Collections.Messages()
col.fetch()
```
You should see backbone talking to the resource server in the server shell
```
127.0.0.1 - - [20/Nov/2012 01:17:15] "GET /messages HTTP/1.1" 200 -
```

You can inspect the results using
```
col.models
```

Using fetch() only works if your schema includes a link with `rel=instances`

#### Create a new message

```
var msg = new App.Models.Message({recipient:"01234567890", text:"test message"})
msg.attributes
```

At that point the message is not saved yet, you can verify by using
```
msg.isNew()
```

You can save it on the server using 
```
msg.save()
```

You can verify that the message was sent to the server in the server shell
```
127.0.0.1 - - [20/Nov/2012 01:23:24] "POST /messages HTTP/1.1" 201 -
```

Now you should have an id for the message and it shouldn't be marked as new anymore.
```
msg.id
msg.isNew()
```

#### Fetch an existing message

Create a message with the `id` of the message to fetch
```
var msg = new App.Models.Message({id: 3})
```

The message is not marked as new as it has an id.  
We can then fetch the actual message from the server using  
```
msg.fetch()
msg.attributes()
```

You can see the query in the server shell again
```
127.0.0.1 - - [20/Nov/2012 01:25:41] "PUT /messages/3 HTTP/1.1" 200 -
```

#### Update a message

Once you have a message object, you can update it using `save`.

```
> msg.attributes.recipient
"01234567890"
> msg.save({recipient:"00123456789"})
> msg.attributes.recipient
"00123456789"
```

This is done by doing a `PUT` on the server
```
127.0.0.1 - - [20/Nov/2012 01:33:35] "PUT /messages/3 HTTP/1.1" 200 -
```

#### Delete a message

Simply use `destroy` on the object
```
msg.destroy()
```

And see the `DELETE` happening on the server
```
127.0.0.1 - - [20/Nov/2012 01:34:48] "DELETE /messages/3 HTTP/1.1" 204 -
```

---

## resourceserver

Class to implement the REST api of resources defined in a schema.  
Supports creation, update, retrieval, deletion, listing of instances and schema.  

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
$ curl -i -X POST    http://0.0.0.0:5000/messages -d '{"recipient":"0123456780", "text":"test message"}' \
	   -H "Content-Type: application/json"
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

#### Trying to create a message in json with invalid data

```
$ curl -i -X POST    http://0.0.0.0:5000/messages  -d '{"recipient":"01234567890", "text":"test message}' -H "Content-Type: application/json"
HTTP/1.0 400 BAD REQUEST
Content-Type: application/json
Content-Length: 90
Server: Werkzeug/0.8.3 Python/2.7.3
Date: Tue, 20 Nov 2012 00:23:05 GMT

{
  "error": "Invalid data: Unterminated string starting at: line 1 column 35 (char 35)"
}
```

# Dependencies

## Required

run init.sh in dependencies

## Optional

### flasksqlalchemymodelgenerator and resourceserver

flask-sqlalchemy is required, use flasksqlalchemy-requirements.txt with virtualenv

### backbonemodelgenerator

jinja2 is required, comes with flask if you use the flasksqlalchemy-requirements.txt
