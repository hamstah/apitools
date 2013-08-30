from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy, orm

from .modelgenerator import ModelGenerator, UnknownPropertyError, MissingRequiredPropertyError
from .validation import generate_validator_for_property, ValidationError

class FlaskSQLAlchemyModelGenerator(ModelGenerator):

    def __init__(self):
        ModelGenerator.__init__(self)

    def generate(self, db, schema):

        attribs = ModelGenerator.generate(self, schema)
        key_name = attribs["key_name"]
        properties = schema.get("properties",{})

        # add columns and validators from the schema properties
        for property_name, property_schema in list(properties.items()):
            attribs[property_name] = self.generate_column(db, property_schema, 
                                                          property_name==key_name)

            validator = generate_validator_for_property(property_name, property_schema)
            if validator:
                attribs[validator.__name__] = orm.validates(property_name)(validator)

        model = type(str(schema["name"]),(db.Model,), attribs)
        return model

    def generate_column(self, db, schema, primary):
        # convert from json-schema type to SQLAlchemy type
        sqla_type = {"integer":db.Integer,
                     "number":db.Float,
                     "boolean":db.Boolean,
                     "string":db.String
                     }[schema["type"]]

        # create the column
        required = schema.get("required", False)
        return db.Column(sqla_type, nullable=not required,primary_key=primary)


if __name__ == "__main__":

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
    db = SQLAlchemy(app)

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
        print("0 not allowed")
        assert False
    except ValidationError as e:
        pass

    try:
        test.reference = -7
        print("<0 not allowed")
        assert False
    except ValidationError as e:
        pass

    # > 5 isn't allowed
    try:
        test.reference = 7
        print(">6 not allowed")
        assert False
    except ValidationError as e:
        pass

    # 6 is allowed
    test.reference = 6

    try:
        test.reference = 5
        print("5 not divisible by 2")
        assert False
    except ValidationError as e:
        pass

    try:
        test.name = "a"
        print("too short")
        assert False
    except ValidationError as e:
        pass

    try:
        test.name = "12345678"
        print("too long")
        assert False
    except ValidationError as e:
        pass

    test.name = "a2c4"

    try:
        test.code = "aaaa"
        print("wrong pattern")
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

