from flask import Flask, request, abort, jsonify
from sqlalchemy import exc
from flask.ext.sqlalchemy import SQLAlchemy, orm

import json
import re
import sys

from .flasksqlalchemymodelgenerator import FlaskSQLAlchemyModelGenerator
from .modelgenerator import UnknownPropertyError, MissingRequiredPropertyError, ReadOnlyPropertyError
from .validation import ValidationError
from . import utils

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

    def save(self):
        """Shortcut to save a changes to the database"""
        self.db.session.commit()

    def host_str(self):
        return "http://%s:%d"%(self.host, self.port)

    def add_resource(self, schema):
        """Add the resource to the list of resources the server can handle"""

        # generate and store the model
        model = self.model_generator.generate(self.db, schema)
        setattr(self, schema["name"], model)

        def add_route(fn, methods=["GET"]):
            # transform the link href into a flask route
            href = utils.url_to_flask_route(model.links[fn.__name__.replace("r_","")], model)
            fn.methods = methods
            self.app.add_url_rule(href, fn.__name__, fn)

        def input_error(error, code=400):
            ret = jsonify({"error":str(error)})
            ret.status_code = code
            return ret

        # generate routes automatically for some of the links
        if "instances" in model.links:
            # returns all the instances of the model
            def r_instances(**kwargs):
                return (json.dumps([res.properties_values() for res in model.query.all()]), 
                        200,
                        {"Content-Type":"application/json"})
            add_route(r_instances)

        if "self" in model.links:
            # returns an instance of the object by key
            # if used with OPTIONS, returns the json-schema
            def r_self(**kwargs):
                if len(list(kwargs.keys())) != 1:
                    raise Exception("Self link with multiple arguments not supported")
                res = model.query.filter_by(**kwargs).first()
                if not res:
                    abort(404)

                if request.method == "GET":
                    return jsonify(res.properties_values())
                elif request.method == "OPTIONS":
                    return jsonify(res.schema)
                elif request.method == "DELETE":
                    self.delete(res)
                    return ("",204)
                elif request.method == "PUT":
                    if len(list(request.form.items())):
                        attribs = dict(list(request.form.items()))
                    elif len(request.data):
                        attribs = json.loads(request.data)
                    else:
                        return input_error("empty body")
                    print(attribs)
                    for key, value in list(attribs.items()):
                        # don't let the update change readonly
                        # properties like the primary key
                        if key not in res.properties:
                            return input_error(UnknownPropertyError(res.__class__.__name__, key))

                        if not res.updatable(key):
                            return input_error(ReadOnlyPropertyError(res.__class__.__name__, key))
                        try:
                            setattr(res, key, value)
                        except exc.IntegrityError as error:
                            # one of the constraint failed
                            return input_error(error)
                        except ValidationError as error:
                            return input_error(error)

                    self.save()
                    return ("",200)
            add_route(r_self, ["GET", "OPTIONS", "DELETE","PUT"])

        if "create" in model.links:
            # creates a new instance
            def r_create(**kwargs):
                try:
                    # this is ok as the model checks the input in __init__

                    if len(list(request.form.items())):
                        attribs = dict(list(request.form.items()))
                    elif len(request.data):
                        attribs = json.loads(request.data)
                    else:
                        return input_error("empty body")
                    new_obj = model(**attribs)

                    # saves the object and return
                    self.add(new_obj)
                    ret = jsonify(new_obj.key_dict())
                    ret.status_code = 201
                    ret.headers["Location"] = "%s%s"%(self.host_str(),new_obj.self_link())
                    return ret
                except ValueError as error:
                    # invalid json
                    return input_error("Invalid data: %s"%error)
                except ValidationError as error:
                    return input_error(error)
                except exc.IntegrityError as error:
                    # should check for different types of failures and return 400
                    # can be duplicate on the primary key, or one of the
                    # constraints on the data failing
                    input_error(error, 409)
                except MissingRequiredPropertyError as error:
                    return input_error(error)
                except UnknownPropertyError as error:
                    return input_error(error)
                except ReadOnlyPropertyError as error:
                    return input_error(error)

            add_route(r_create, ["POST"])
        return model

if __name__ == "__main__":
    
    server = ResourceServer()

    for path in sys.argv[1:]:
        schema = json.loads(open(path).read())
        server.add_resource(schema)
        print("Added %s"%schema["name"])

    server.db.create_all()
    server.run(debug=True)
    
