import json
from . import utils

from .validation import generate_validator_for_property


class UnknownPropertyError(Exception):
    def __init__(self, type_name, property_name):
        Exception.__init__(self, "%s does not have a '%s' property" % (
            type_name, property_name))
        self.property_name = property_name


class MissingRequiredPropertyError(Exception):
    def __init__(self, type_name, property_name):
        Exception.__init__(self, "%s is required in %s" %(
            property_name, type_name))
        self.property_name = property_name


class ReadOnlyPropertyError(Exception):
    def __init__(self, type_name, property_name):
        Exception.__init__(self, "%s is read only in %s" %(
            property_name, type_name))
        self.property_name = property_name


class Model(object):

    def __init__(self, **kwargs):
        if not hasattr(self, "__properties"):
            raise Exception("Missing properties, can't validate instance")

        properties = getattr(self, "__properties")

        # set the attributes
        for key, value in list(kwargs.items()):
            setattr(self, key, value)

        # check that all the required args are present
        for required_prop in [prop_key for prop_key, prop_schema in list(properties.items())
                              if prop_schema.get("required", False)]:
            if required_prop not in list(kwargs.keys()):
                raise MissingRequiredPropertyError(
                    self.__class__.__name__, required_prop)

    def __repr__(self):
        properties = getattr(self, "__properties")
        return "<%s %s>" % (self.__class__.__name__,
                            ','.join(["%s=%s" % (attr_name, getattr(self, attr_name))
                                      for attr_name in sorted(properties.keys())]))

    def __setattr__(self, name, value):
        """Validates the attribute before accepting it.
        Can throw the following exceptions
        * UnknownPropertyError if the attribute is invalid
        * MissingRequiredPropertyError if a required attribute is omitted
        * ValidationError if the attribute value isn't valid
        """
        assert hasattr(self, "__validators") and hasattr(self, "__properties")
        validators = getattr(self, "__validators")
        properties = getattr(self, "__properties")

        if name not in properties:
            raise UnknownPropertyError(self.__class__.__name__, name)

        # validates the data
        if name in validators:
            validators[name](self, name, value)

        self.__dict__[name] = value

    def to_dict(self):
        return {key: getattr(self, key) for key in list(getattr(self, "__properties").keys())}


class ModelGenerator:

    def __init__(self):
        pass

    def generate(self, schema):

        def init(obj, **kwargs):
            # set the attributes
            for key, value in list(kwargs.items()):
                if key not in properties:
                    raise UnknownPropertyError(schema["name"], key)
                    if key == key_name and implicit_key:
                        raise ReadOnlyPropertyError(schema["name"], key)

                setattr(obj, key, value)

            # check that all the required args are present
            for required_prop in [prop_key for prop_key, prop_schema in list(properties.items())
                                  if prop_schema.get("required", False)]:
                if required_prop not in list(kwargs.keys()):
                    raise MissingRequiredPropertyError(
                        schema["name"], required_prop)

        properties = schema.get("properties", {})
        implicit_key = False
        attribs = {
            "__init__": init,
            "__repr__": lambda obj:
            "<%s %s>" % (obj.__class__.__name__,
                         ','.join(["%s=%s" % (attr_name, getattr(obj, attr_name))
                                   for attr_name in list(properties.keys())])),
            "properties": properties,
            "properties_values": lambda obj:
            dict((
                k, v) for k, v in obj.__dict__.items(
                ) if k in list(properties.keys())),
            "updatable": lambda obj, key:
            key in list(properties.keys()) and key != obj.key_name,
            "writable": lambda obj, key:
            key in list(properties.keys()) and key != obj.key_name or not obj[
                "implicit_key"],
            "implicit_key": implicit_key,
            "key_value": lambda obj:
            getattr(obj, obj.key_name),
            "key_dict": lambda obj:
            {obj.key_name: obj.key_value()},
            "schema": schema,
            "links": {},
        }

        # process the links section
        rel_links = {"root": (
            "/", "/")}  # provide default root if none is given
        for schema_link in schema.get("links", []):
            rel = schema_link.get("rel", None)
            if not rel:
                continue
                href = schema_link.get("href", "")
                rel_links[rel] = (href, utils.url_to_template(href))

        # store the links
        # - the json-schema format with root in links[<rel>]
        # - add helper lambdas to generate actual links under link_<rel>
        root = attribs["links"]["root"] = rel_links["root"]
        for rel, (href, template_href) in list(rel_links.items()):
            if rel != "root":
                (json_base, template_base) = root
                if href:
                    json_base += "/" + href
                    template_base += "/" + template_href
                    attribs["links"][rel] = json_base
                    attribs["%s_link" % rel] = lambda obj, template_base=template_base: template_base % obj.properties_values()

        # find the primary key from the "self" link
        # or create one with a new column
        try:
            key_name = utils.get_resource_key(schema)
        except Exception:
            key_name = "id"
            while key_name in list(properties.keys()):
                key_name = '_' + key_name

        # add a new property for the key if it doesn't exist
        if key_name not in properties:
            properties[key_name] = {"type": "integer", "minimum": 0}
            implicit_key = True

        attribs["key_name"] = key_name
        return attribs

    def generate_model(self, schema):
        properties = schema.get("properties", {})
        attribs = {
            "__validators": {},
            "__properties": properties,
        }

        # add columns and validators from the schema properties
        for property_name, property_schema in list(properties.items()):
            attribs[property_name] = property_schema.get("default", None)
            validator = generate_validator_for_property(
                property_name, property_schema)
            if validator:
                attribs["__validators"][property_name] = validator

        return type(str(schema["name"]), (Model,), attribs)

if __name__ == "__main__":
    generator = ModelGenerator()
    schema = json.loads(open("data/schemas/book.json").read())
    Book = generator.generate_model(schema)

    print(Book(authors="hhh", isbn="1234567890123", title="jjj"))
