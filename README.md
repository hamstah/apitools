Tools to play with json-schemas defined APIs.

These tools are based on json-schema draft 3 from http://tools.ietf.org/html/draft-zyp-json-schema-03
Not all features of the schema are supported and probably won't be.
Handling of not supported feature varies between the different tools.

All these tools are proofs of concept and work in progress, they need more extensive testing and documentation.

# datagenerator 

Class to generate random values given a json-schema.  
Doesn't support all json-schema monstruousities, only a subset I find useful.  
See TODO.md for what is likely to be implemented next.  

## Examples

```python
from datagenerator import DataGenerator

generator = DataGenerator()
```

### Basic

Generate random values of each basic type using

```python
>>> generator.random_value("string")
'Olzq3LV'
>>> generator.random_value("number")
-6.675904074356879
>>> generator.random_value("integer")
30
>>> generator.random_value("boolean")
True

```

### Basic with constraints

`number`

```python
>>> generator.random_value({"type":"number", "minimum":30})
32.34295327292445
>>> generator.random_value({"type":"number", "maximum":30})
-35.80704939879546
>>> generator.random_value({"type":"number", "maximum":30, "minimum":12})
16.45747265846327
```

`integer` supports `minimum` and `maximum` like `number` and more
```python
>>> generator.random_value({"type":"integer", "maximum":30, "divisibleBy":4, "minimum":12})
24
>>> generator.random_value({"type":"integer", "maximum":30, "exclusiveMaximum":True, "minimum":28})
29
```
(same for `exclusiveMinimum`)

`string` supports `minLength`, `maxLength`, `pattern` (ignores `minLength` and `maxLength` if `pattern` is used)
```python
>>> generator.random_value({"type":"string", "maxLength":20, "minLength":15})
'VytPCEdAImX11188HU'
>>> generator.random_value({"type":"string", "pattern":"[0-9]{3}[a-zA-Z]{2,5}"})
u'806FoNP'
```

`boolean` doesn't have any constraints.

### Arrays

Without constraints the array size will be picked the same way as a random `integer`.  
Each item in the array is generated using the default generator for the type given in `items`.
```python
>>> generator.random_value({"type":"array", "items": {"type":"string"}})
[
	'39yxcpvS5tfPf6O', 
	'sNDk7SlGNQstxxx', 
	'nPcRSD9yIP7j ', 
	'PWP7KQfjc1', 
	'tt6F6Z2YEp'
]
```

`minItems`, `maxItems` and `uniqueItems` are supported

The type of object in `items` can be anything that the generator knows about, either one of the basic types
or a user defined one available from the generator's schemas store. 

```python
from schemasstore import SchemasStore

...
>>> from schemasstore import SchemasStore
>>> store = SchemasStore()
>>> generator.schemas_store = store
>>> store.add_schema({"type":"integer", "name":"small_integer", "minimum":0,"maximum":9})
True
>>> generator.random_value({"type":"array", "uniqueItems":True, "minItems":10, "items":{"type":"small_integer"}})
[0, 7, 2, 5, 3, 6, 1, 4, 8, 9]
```

See [datagenerator](https://github.com/hamstah/apitools/blob/master/datagenerator.py) for other examples.

### Objects

Objects can be generated the same way as the other types.

Example generating [search_result.json](https://github.com/hamstah/apitools/blob/master/data/schemas/search_result.json)
```python
>>> store.load_folder("data/schemas/")
>>> generator.random_value("search_result")
{u'price': 21.980325774975253, u'name': 'wdvfXYrrt', u'reference': 26}
```

Generating arrays of objects is fine as well
```python
>>> generator.random_value({"type":"array", "maxItems":3, "minItems":2, "items":{"type":"search_result"}})
[
    {u'price': 20.304440535786522, u'name': 'VUIgjaPbs', u'reference': 40}, 
	{u'price': 28.45387747055259, u'name': 'JTycBU1V78X1S', u'reference': 27}
]
```

Or generating objects with arrays of other objects in them, see
[search_resuts](https://github.com/hamstah/apitools/blob/master/data/schemas/search_results.json) 
with an array of [search_result](https://github.com/hamstah/apitools/blob/master/data/schemas/search_result.json)
```python
>>> generator.random_value("search_results")
{
    u'total_results': 41, 
	u'total_pages': 26, 
	u'current_page': 33, 
	u'items_per_page': 27, 
	u'results': [
	    {u'price': 26.218704680177446, u'name': 'B4p1Z1pOFQO', u'reference': 38}, 
		{u'price': 21.205089550441276, u'name': 'FQPHdLds', u'reference': 7}, 
		{u'price': 20.610536930894398, u'name': '8D862p1XVupP', u'reference': 38}, 
		{u'price': 9.543934434058526, u'name': 'PmqBA0e DIWisf', u'reference': 32}
	]
}
```

### Schemas

Why not generate random schemas?
```python
>>> r_schema = generator.random_schema()
>>> r_schema
{
    'type': 'object', 
	'properties': {
	    u'viYXjhu': {'required': False, 'type': 'boolean'}, 
		u'TO': {'required': False, 'type': 'string'}, 
		u'NTSd': {'required': False, 'type': 'string'}, 
		u'WjaL': {'required': False, 'type': 'string'}, 
		u'PtvhZ': {'required': False, 'type': 'boolean'}
	}, 
	'name': u'zJllGkKosmocOVO'
}
```
And then generate an array of random values of it
```python
>>> store.add_schema(r_schema)
True
>>> generator.random_value({"type":"array", "minItems":1, "maxItems":3, "items":{"type":"zJllGkKosmocOVO"}})
[
	{u'TO': 'jamKFpdwY'}, 
	{u'WjaL': '8LnibWUdsSI', u'PtvhZ': True}, 
	{}
]
```

## Notes on the generation

All the values are generated using the `random` module, so please don't use the generate values for anything
requiring reliable randomness == **don't use it to generate passwords**.

To generate the data, the generator has to limit the range of possible values, so the values generated don't
vary too wildly. The ranges are controlled by variables in `DataGenerator`. Feel free to tweak them, especially
if you need values that don't fall into those ranges without having to set both minimum and maximum on your 
properties.

---

# urlsgenerator

Class to generate links defined in the links section of a json-schema.

## Example

Generate links from [book.json](https://github.com/hamstah/apitools/blob/master/data/schemas/book.json)

Input
```javascript
...
	"isbn" : {
	    "type":"string",
	    "required":true,
	    "pattern":"^\\d{12}(\\d|X)$"
	}

    },
    "links" : [
	{
	    "rel":"self",
	    "href":"books/{isbn}"
	},
	{
	    "rel":"instances",
	    "href": "books"
	}
    ]
...

```

Output
```python
{
    u'instances': [u'books'], 
    u'self'     : [u'books/525259838909X']
}
```

`{isbn}` got replaced by a random value `525259838909X` satisfying the constraints on `isbn` (matches the regex).

---

# invaliddatagenerator

Class to generate invalid data for a given schema

Basically does the opposite of datagenerator. WIP, needs documentation and examples.

---

# modelgenerator

Base class to generate models from a schema, nothing too visible on its own, check `resourceserver`.

---

# flasksqlalchemymodelgenerator

Generate SQLAlchemy models to be used with flask-sqlalchemy from a schema. Uses `modelgenerator`. 
Used in `resourceserver` to store and query items.

---

# backbonemodelgenerator

Generate models and collections for Backbone.js from a schema.  
The models generated use the primary key defined in the `rel=self` link or `id` by default.  
To be able to use collections, make sure your schema has a `rel=instances` link or `fetch` won't work.  

## Usage

```bash
$ python backbonemodelgenerator.py -h
Usage: backbonemodelgenerator.py jsonfile1 [jsonfile2]...

Options:
  -h, --help            show this help message and exit
  -t OUTPUT_TYPE, --type=OUTPUT_TYPE
                        Output type (js|wrapped|html)
```

## Output types

### js

Outputs only the js code for the models/collections

```bash
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

### wrapped

Wraps the js code into `$(document).ready()`

```bash
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

### html

Same as wrapped but generate a whole html page including jQuery, Backbone and Underscore to easily test.

## Example usage

### Setup

You can use it with resource server for example
```bash
$ mkdir static
$ python backbonemodelgenerator.py -t html data/schemas/message.json > static/index.html
$ python resourceserver.py data/schemas/message.json
Added message
 * Running on http://0.0.0.0:5000/
```

Now open your browser at http://0.0.0.0:5000/static/index.html
Open your js console to start playing

### Create a collection and fetch them

```javascript
var col = new App.Collections.Messages()
col.fetch()
```
You should see backbone talking to the resource server in the server shell
```bash
127.0.0.1 - - [20/Nov/2012 01:17:15] "GET /messages HTTP/1.1" 200 -
```

You can inspect the results using
```javascript
col.models
```

Using fetch() only works if your schema includes a link with `rel=instances`

### Create a new message

```javascript
var msg = new App.Models.Message({recipient:"01234567890", text:"test message"})
msg.attributes
```

At that point the message is not saved yet, you can verify by using
```javascript
msg.isNew()
```

You can save it on the server using 
```javascript
msg.save()
```

You can verify that the message was sent to the server in the server shell
```bash
127.0.0.1 - - [20/Nov/2012 01:23:24] "POST /messages HTTP/1.1" 201 -
```

Now you should have an id for the message and it shouldn't be marked as new anymore.
```javascript
msg.id
msg.isNew()
```

### Fetch an existing message

Create a message with the `id` of the message to fetch
```javascript
var msg = new App.Models.Message({id: 3})
```

The message is not marked as new as it has an id.  
We can then fetch the actual message from the server using  
```javascript
msg.fetch()
msg.attributes()
```

You can see the query in the server shell again
```bash
127.0.0.1 - - [20/Nov/2012 01:25:41] "PUT /messages/3 HTTP/1.1" 200 -
```

### Update a message

Once you have a message object, you can update it using `save`.

```javascript
> msg.attributes.recipient
"01234567890"
> msg.save({recipient:"00123456789"})
> msg.attributes.recipient
"00123456789"
```

This is done by doing a `PUT` on the server
```bash
127.0.0.1 - - [20/Nov/2012 01:33:35] "PUT /messages/3 HTTP/1.1" 200 -
```

### Delete a message

Simply use `destroy` on the object
```javascript
msg.destroy()
```

And see the `DELETE` happening on the server
```bash
127.0.0.1 - - [20/Nov/2012 01:34:48] "DELETE /messages/3 HTTP/1.1" 204 -
```

---

# resourceserver

Class to implement the REST api of resources defined in a schema.  
Supports creation, update, retrieval, deletion, listing of instances and schema.  

## Usage

Run the server using
```bash
$ python resourceserver.py [jsonfile1, jsonfile2, ...]
```

## Example using data/schemas/message.json

```bash
$ python resourceserver.py data/schemas/message.json
Added message
 * Running on http://0.0.0.0:5000/
```

### Create a new message

```bash
$ curl -i -X POST    http://0.0.0.0:5000/messages -d "recipient=07771818335&text=nice message"
$ curl -i -X POST    http://0.0.0.0:5000/messages -d '{"recipient":"01234567890", "text":"test"}' \
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

### List messages

```bash
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

### Retrieve a message

```bash
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

### Get the json-schema of a message

```bash
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

### Update a message

Supports partial updates

```bash
$ curl -i -X PUT     http://0.0.0.0:5000/messages/2 -d 'recipient=07771818336'
$ curl -i -X PUT     http://0.0.0.0:5000/messages/1 -d '{"text":"foo"}' \
          -H "Content-Type: application/json"
HTTP/1.0 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 0
Server: Werkzeug/0.8.3 Python/2.7.3
Date: Sun, 18 Nov 2012 19:38:02 GMT
```

### Delete a message

```bash
$ curl -i -X DELETE  http://0.0.0.0:5000/messages/2
HTTP/1.0 204 NO CONTENT
Content-Type: text/html; charset=utf-8
Content-Length: 0
Server: Werkzeug/0.8.3 Python/2.7.3
Date: Sun, 18 Nov 2012 19:38:38 GMT
```

## Errors examples

### Trying to set an implicit key

The message.json doesn't define an explicit primary key, but defines `id` as the key in the `rel=self` link.  
Each message then gets an additional `id` key managed by the server.  
Trying to set or update the `id` results in errors  

```bash
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
### Trying to create or update unknown properties

```bash
$ curl -i -X POST    http://0.0.0.0:5000/messages   -d "recipient=07771818335&tet=test&haxxy=foo"
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

### Trying to create or update properties with values not respecting constraints

```bash
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

### Trying to create a message without all the required properties

```bash
$ curl -i -X POST    http://0.0.0.0:5000/messages -d "recipient=012345678901"HTTP/1.0 400 BAD REQUEST
Content-Type: application/json
Content-Length: 44
Server: Werkzeug/0.8.3 Python/2.7.3
Date: Sun, 18 Nov 2012 20:06:00 GMT

{
  "error": "text is required in message"
}
```

### Trying to create a message in json with invalid data

```bash
$ curl -i -X POST    http://0.0.0.0:5000/messages  -d '{"recipient":"01234567890", "text":"test}' -H "Content-Type: application/json"
HTTP/1.0 400 BAD REQUEST
Content-Type: application/json
Content-Length: 90
Server: Werkzeug/0.8.3 Python/2.7.3
Date: Tue, 20 Nov 2012 00:23:05 GMT

{
  "error": "Invalid data: Unterminated string starting at: line 1 column 35 (char 35)"
}
```

## Primary keys

Each model needs a primary key.
There are 3 ways to define the primary key of the model:

If there is no `rel=self` link, an additional `id` (or appended with as many `_` as 
necessary to make the name unique) attribute is created. This type of key is called *implicit* and can
only be set by the server (read only).


If there is a `rel=self` link and it contains a `{variable}` part, the variable name is used as the primary key.
* If `variable` is the name of an existing property, this property is used as the primary key, and can be updated
( *explicit key* )
* Otherwise an *implicit* key is created using the `variable` name (stil read-only).

### Example of an explicit key

This schema uses `isbn` as the explicit key. Instances can be created using a specific `isbn`, and its value
can be updated.

```javascript
...
	"isbn" : {
	    "type":"string",
	    "required":true,
	    "pattern":"^\\d{12}[\\d|X]$"
	}

    },
    "links" : [
	{
	    "rel":"self",
	    "href":"books/{isbn}"
	},
...
```

### Example of implicit key

This schema defines an *implicit* key `order_id` (assuming no property is called `order_id`).
```javascript
...
    "links" : [
        {
            "rel":"self",
            "href":"{order_id}"
        },
...
```

# Dependencies

## Optional

### datagenerator, invaliddatagenerator and urlgenerator

Use `rstr` hosted in a mercurial repo on bitbucket. Run `init.sh` in dependencies to fetch it.
If you don't have mercurial, `apt-get install mercurial` should help.

### flasksqlalchemymodelgenerator and resourceserver

flask-sqlalchemy is required, use flasksqlalchemy-requirements.txt with virtualenv

### backbonemodelgenerator

jinja2 is required, comes with flask if you use the flasksqlalchemy-requirements.txt
