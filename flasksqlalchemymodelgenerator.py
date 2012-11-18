from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy, orm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

from modelgenerator import ModelGenerator, ValidationException

class FlaskSQLAlchemyModelGenerator(ModelGenerator):

      def __init__(self):
            ModelGenerator.__init__(self)

      def generate(self, db, schema):

            attribs = {
                  # default columns for all models
                  "id" : db.Column(db.Integer, primary_key=True),

                  # utils
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
                         "boolean":db.Boolean}[schema["type"]]

            # create the column
            required = "required" in schema and schema["required"]
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
                        "divisibleBy":2
                        },
                  "in_stock": {
                        "type":"boolean",
                        "required":True
                        },
                  "price": {
                        "type":"number",
                        "required":True,
                        "minimum":0
                        }
                  }
            }

      generator = FlaskSQLAlchemyModelGenerator()
      model = generator.generate(db,schema)
      
      
      test = model()

      test.reference = 2

      # <= 0 isn't allowed
      try:
            test.reference = 0
            print "0 not allowed"
            assert False
      except ValidationException as e:
            pass
      
      try:
            test.reference = -7
            print "<0 not allowed"
            assert False
      except ValidationException as e:
            pass

      # > 5 isn't allowed
      try:
            test.reference = 7
            print ">6 not allowed"
            assert False
      except ValidationException as e:
            pass

      # 6 is allowed
      test.reference = 6

      try:
            test.reference = 5
            print "5 not divisible by 2"
            assert False
      except ValidationException as e:
            pass      

      # try:
      #       db.session.commit()
      # except: 
      #       print "Creating the tables first"
      #       db.session.rollback()
      #       db.create_all()
      #       db.session.commit()

