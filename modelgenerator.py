import re

import utils

class ValidationError(Exception):
      def __init__(self, type_name, value, message):
            Exception.__init__(self, "'%s' is an invalid %s value: %s"%(value, type_name, message))

class UnknownPropertyError(Exception):
      def __init__(self, type_name, property_name):
            Exception.__init__(self, "%s does not have a '%s' property"%(type_name, property_name))
            self.property_name = property_name

class MissingRequiredPropertyError(Exception):
      def __init__(self, type_name, property_name):
            Exception.__init__(self, "%s is required in %s"%(property_name,type_name))
            self.property_name = property_name

class ReadOnlyPropertyError(Exception):
      def __init__(self, type_name, property_name):
            Exception.__init__(self, "%s is read only in %s"%(property_name,type_name))
            self.property_name = property_name

class ModelGenerator:

      def __init__(self):
            pass
      
      def generate(self, schema):

            def init(obj, **kwargs):
                  # set the attributes
                  for key, value in kwargs.items():
                        if key not in properties:
                              raise UnknownPropertyError(schema["name"],key)
                        if key == key_name and implicit_key:
                              raise ReadOnlyPropertyError(schema["name"],key)

                        setattr(obj, key, value)

                  # check that all the required args are present
                  for required_prop in [prop_key for prop_key, prop_schema in properties.items()
                                        if prop_schema.get("required",False)]:
                        if required_prop not in kwargs.keys():
                              raise MissingRequiredPropertyError(schema["name"], required_prop)

            properties = schema.get("properties",{})
            implicit_key = False
            attribs = {
                  "__init__": init,
                  "__repr__" : lambda obj:
                        "<%s %s>"%(obj.__class__.__name__,
                                   ','.join(["%s=%s"%(attr_name, getattr(obj, attr_name))
                                             for attr_name in properties.keys()])),
                  "properties": properties,
                  "properties_values": lambda obj:
                        dict((k, v) for k,v in obj.__dict__.iteritems() if k in properties.keys()),
                  "updatable":lambda obj, key:
                        key in properties.keys() and key != obj.key_name,
                  "writable": lambda obj, key:
                        key in properties.keys() and key != obj.key_name or not obj["implicit_key"],
                  "implicit_key": implicit_key,
                  "key_value" : lambda obj:
                        getattr(obj, obj.key_name),
                  "key_dict": lambda obj:
                        {obj.key_name: obj.key_value()},
                  "schema": schema,
                  "links":{},
                  }

            # process the links section
            rel_links = {"root":("/","/")} # provide default root if none is given
            for schema_link in schema.get("links",[]):
                  rel = schema_link.get("rel",None)
                  if not rel:
                        continue
                  href = schema_link.get("href","")
                  rel_links[rel] = (href, utils.url_to_template(href))

            # store the links
            # - the json-schema format with root in links[<rel>]
            # - add helper lambdas to generate actual links under link_<rel>
            root = attribs["links"]["root"] = rel_links["root"]
            for rel, (href, template_href) in rel_links.items():
                  if rel != "root":
                        (json_base, template_base) = root
                        if href:
                              json_base += "/"+href
                              template_base += "/"+template_href
                        attribs["links"][rel] = json_base
                        attribs["%s_link"%rel] = lambda obj, template_base=template_base: template_base%obj.properties_values()

            # find the primary key from the "self" link
            # or create one with a new column
            try:
                  key_name = utils.get_resource_key(schema)
            except Exception as e:
                  key_name = "id"
                  while key_name in properties.keys():
                        key_name = '_' + key_name

            # add a new property for the key if it doesn't exist
            if key_name not in properties:
                  properties[key_name] = {"type":"integer","minimum":0}
                  implicit_key = True

            attribs["key_name"] = key_name
            return attribs

      def generate_validator(self, name, schema):
            attr_name = "%s_tests"%schema["type"]
            if not hasattr(self, attr_name):
                  return None

            # get the validator functions specific to the type
            method = getattr(self, attr_name)
            tests = method(schema)
            return self.generate_validator_from_tests(name, schema, tests)

      def generate_validator_from_tests(self, name, schema, tests):
            # only keep the relevant tests
            found_tests = [test for test in tests.items()
                           if test[0] in schema or test[0].startswith("__")]

            # if no tests are found, no validator is required
            if len(found_tests) == 0:
                  return None
            
            def fn(self, key, value):
                  for test_type, (test_fn, message) in sorted(found_tests,
                                                              key=lambda test: test[0]):
                        res = False
                        test_value = schema.get(test_type, None)
                        if not test_type.startswith("__"):
                              res = test_fn(value,test_value)
                        else:
                              res = test_fn(value)

                        if not res:
                              raise ValidationError(name, value, message%{"test_type":test_type,
                                                                          "test_value":test_value,
                                                                          "value":value})
                  return value
            fn.__name__ = str("validate_%s"%(name))
            return fn

      def number_tests(self, schema):
            tests = self.numeric_tests(schema)
            tests["__isNumber"] = (lambda value: isinstance(value, (int, long, float)), "'%(value)s' is not a number")
            return tests

      def integer_tests(self, schema):
            tests = self.numeric_tests(schema)
            tests.update({
                        "__isInt" : (lambda value: isinstance(value, (int, long)), "'%(value)s' is not an integer"),
                        "divisibleBy" : (lambda value, div_by : value%div_by == 0, "not divisible by %(test_value)s")
                        })
            return tests

      def numeric_tests(self, schema):
            message = "%(test_type)s is %(test_value)s"
            
            tests = {
                  "minimum": (lambda value,min_value: value >= min_value, message),
                  "maximum": (lambda value,max_value: value <= max_value, message),
                  "exclusiveMinimum" : (lambda value, is_exclusive: not is_exclusive or value != schema["minimum"], message),
                  "exclusiveMaximum" : (lambda value, is_exclusive: not is_exclusive or value != schema["maximum"], message),              
                  }    
            return tests

      def string_tests(self, schema):
            tests = {
                  "__isString": (lambda value: isinstance(value,basestring), "'%(value)s' is not a string"),
                  "minLength": (lambda value, min_len: len(value) >= min_len, "length must be >= %(test_value)s"),
                  "maxLength": (lambda value, max_len: len(value) <= max_len, "length must be <= %(test_value)s"),                  
                  "pattern": (lambda value, pattern: re.match(pattern, value), "must match %(test_value)r"),
                  }
            return tests

