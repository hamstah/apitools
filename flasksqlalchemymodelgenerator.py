from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy, orm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

from modelgenerator import ModelGenerator, ValidationError, UnknownPropertyError, MissingRequiredPropertyError

class FlaskSQLAlchemyModelGenerator(ModelGenerator):

    def __init__(self):
        ModelGenerator.__init__(self)

    def generate(self, db, schema):

        def init(obj, **kwargs):
            # set the attributes
            for key, value in kwargs.items():
                if key not in properties:
                    raise UnknownPropertyError(schema["name"],key)
                setattr(obj, key, value)

            # check that all the required args are present
            for required_prop in [prop_key for prop_key, prop_schema in properties.items()
                                  if prop_schema.get("required",False)]:
                if required_prop not in kwargs.keys():
                    raise MissingRequiredPropertyError(schema["name"], required_prop)


        attribs = {
            # default columns for all models
            "id" : db.Column(db.Integer, primary_key=True),

            # utils
            "__init__": init,
            "__repr__" : lambda obj:
            "<%s %s>"%(obj.__class__.__name__,
                       ','.join(["%s=%s"%(attr_name, getattr(obj, attr_name))
                                 for attr_name in properties.keys()]))
            }

        properties = schema.get("properties",{})
        # add columns and validators from the schema properties
        for property_name, property_schema in properties.items():
            column = self.generate_column(db, property_name, property_schema)
            attribs[property_name] = column

            validator = self.generate_validator(property_name, property_schema)
            if validator:
                attribs[validator.__name__] = orm.validates(property_name)(validator)

        return type(schema["name"], (db.Model,), attribs)

    def generate_column(self, db, name, schema):
        # convert from json-schema type to SQLAlchemy type
        sqla_type = {"integer":db.Integer,
                     "number":db.Float,
                     "boolean":db.Boolean,
                     "string":db.String
                     }[schema["type"]]

        # create the column
        required = schema.get("required", False)
        return db.Column(sqla_type, nullable=not required)


if __name__ == "__main__":


    schema = {
        "name":"search_result",
        "description":"A product search result",
        "type":"object",
        "properties": {
            "reference": {
                "type":"integer",
                "minimum":0,
                "exclusiveMinimum":True,
                "maximum":6,
                "required":True,
                "divisibleBy":2,
                },
            "in_stock": {
                "type":"boolean",
                "required":True,
                },
            "price": {
                "type":"number",
                "minimum":0
                },
            "name": {
                "type":"string",
                "minLength": 3,
                "maxLength": 7,
                },
            "code": {
                "type":"string",
                "pattern":"^[A-Z0-9]{5}$",
                "required":True,
                },
            }
        }

    generator = FlaskSQLAlchemyModelGenerator()
    model = generator.generate(db,schema)


    test = model(code="12345", in_stock=True, reference=6, price=2.2)

    test.reference = 2

    # <= 0 isn't allowed
    try:
        test.reference = 0
        print "0 not allowed"
        assert False
    except ValidationError as e:
        pass

    try:
        test.reference = -7
        print "<0 not allowed"
        assert False
    except ValidationError as e:
        pass

    # > 5 isn't allowed
    try:
        test.reference = 7
        print ">6 not allowed"
        assert False
    except ValidationError as e:
        pass

    # 6 is allowed
    test.reference = 6

    try:
        test.reference = 5
        print "5 not divisible by 2"
        assert False
    except ValidationError as e:
        pass

    try:
        test.name = "a"
        print "too short"
        assert False
    except ValidationError as e:
        pass

    try:
        test.name = "12345678"
        print "too long"
        assert False
    except ValidationError as e:
        pass

    test.name = "a2c4"

    try:
        test.code = "aaaa"
        print "wrong pattern"
        assert False
    except ValidationError as e:
        pass

    test.code = "ABCD5"


    # try:
    #       db.session.commit()
    # except:
    #       print "Creating the tables first"
    #       db.session.rollback()
    #       db.create_all()
    #       db.session.commit()

