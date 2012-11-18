Utilities to make defining apis easier

## Tools

### datagenerator 

Class to generate random values given a json-schema.
Doesn't support all json-schema monstruousities, only a subset I find useful.
See TODO.md for what is likely to be implemented next.

### urlsgenerator

Class to generate links defined in the links section of a json-schema.

### invaliddatagenerator

Class to generate invalid data for a given schema

### modelgenerator

Base class to generate models from a schema

### flasksqlalchemymodelgenerator

Generate SQLAlchemy models to be used with flask-sqlalchemy from a schema

### resourceserver

Class to implement the REST api of resources defined in a schema.
Supports creation, retrieval, deletion, listing of instances and schema

## Dependencies

### Required
run init.sh in dependencies

### Needed for flasksqlalchemymodelgenerator only

flask-sqlalchemy is required, use flasksqlalchemy-requirements.txt with virtualenv

