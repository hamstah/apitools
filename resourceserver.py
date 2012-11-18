from flask import Flask, request, abort, make_response
from sqlalchemy import exc
from flask.ext.sqlalchemy import SQLAlchemy, orm

import json
import re

from flasksqlalchemymodelgenerator import FlaskSQLAlchemyModelGenerator
import utils

class ResourceServer:

    def __init__(self, name=__name__, host="0.0.0.0", port=5000, database_uri='sqlite:////tmp/test.db'):
        # start flask-sqlalchemy
        self.app = Flask(name)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
        self.db = SQLAlchemy(self.app)

        self.model_generator = FlaskSQLAlchemyModelGenerator()

        # store these here to be able to generate links
        self.host = host
        self.port = port

    def run(self,**kwargs):
        """Shortcut to start the server"""
        kwargs["host"] = self.host
        kwargs["port"] = self.port
        self.app.run(**kwargs)

    def add(self,resource):
        """Shortcut to add the resource instance to the database"""
        self.db.session.add(resource)
        self.db.session.commit()

    def delete(self, resource):
        """Shortcut to remove the resource instance from the database"""
        self.db.session.delete(resource)
        self.db.session.commit()

    def add_resource(self, schema):
        """Add the resource to the list of resources the server can handle"""

        # generate and store the model
        model = self.model_generator.generate(self.db, schema)
        setattr(self, schema["name"], model)

        for link in schema["links"]:
            href = link["href"]
            args = utils.get_url_args(href)

            # transform the link href into a flask route
            for arg_name in args:
                arg_schema = schema["properties"][arg_name]
                flask_type = {"integer":"int",
                              "number":"float",
                              "string":"string"
                              }[arg_schema["type"]]
                href=href.replace("{%s}"%arg_name, "<%s:%s>"%(flask_type, arg_name))
            
            fn = None

            # generate routes automatically for some of the links
            if link["rel"] == "instances":
                # returns all the instances of the model
                def r_instances(**kwargs):
                    return json.dumps([res.properties() for res in model.query.all()])
                r_instances.methods = ["GET"]
                fn = r_instances

            elif link["rel"] == "self":
                if len(args) != 1:
                    raise Exception("Self link with multiple arguments not supported")

                # returns an instance of the object by key
                # if used with OPTIONS, returns the json-schema
                def r_self(**kwargs):
                    res = model.query.filter_by(**kwargs).first()
                    if not res:
                        abort(404)
                    if request.method == "GET":
                        return json.dumps(res.properties())
                    elif request.method == "OPTIONS":
                        return json.dumps(res.schema())
                    elif request.method == "DELETE":
                        self.delete(res)
                        return ("",204)

                r_self.methods = ["GET", "OPTIONS", "DELETE"]
                fn = r_self
                
            elif link["rel"] == "create":
                # creates a new instance
                def r_create(**kwargs):
                    try:
                        # this is ok as the model checks the input in __init__
                        new_obj = model(**dict(request.form.items()))

                        # saves the object and return
                        self.add(new_obj)
                        return (json.dumps(new_obj.key_dict()),
                                201,
                                # TODO cleanup link building
                                {"link":"<http://%s:%d%s>; rel=\"self\""%(self.host,self.port,new_obj.self_link())}
                                )
                    
                    except exc.IntegrityError:
                        # should check for different types of failures and return 400
                        # can be duplicate on the primary key, or one of the
                        # constraints on the data failing
                        abort(409)

                r_create.methods = ["POST"]
                fn = r_create
                
            if fn:
                self.app.add_url_rule(href, fn.__name__, fn)

if __name__ == "__main__":
    
    schema = {
        "name":"book",
        "description":"A book metadata",
        "type":"object",
        "properties": {
            "title": {
                "type":"string",
                "required":True
                },
            
            "isbn" : {
                "type":"string",
                "required":True,
                "pattern":"^\\d{12}[\\d|X]$"
                }

            },
        "links" : [
            {
                "rel":"self",
                "href":"/books/{isbn}",
                },
            {
                "rel":"instances",
                "href": "/books"
                },
            {
                "rel":"create",
                "href":"/books"
                },
            ]
        }

    server = ResourceServer()
    server.add_resource(schema)
    server.db.create_all()

    book_model = server.book

    if len(book_model.query.all()) == 0:
        book = book_model(title="title", isbn="1234567890123")
        server.add(book)


    server.run(debug=True)

    
    
