import re

class ValidationError(Exception):
      def __init__(self, type_name, value, message):
            Exception.__init__(self, "%s is an invalid %s value: %s"%(value, type_name, message))

class UnknownPropertyError(Exception):
      def __init__(self, type_name, property_name):
            Exception.__init__(self, "%s does not have a '%s' property"%(type_name, property_name))

class MissingRequiredPropertyError(Exception):
      def __init__(self, type_name, property_name):
            Exception.__init__(self, "%s is required in %s"%(property_name,type_name))

class ModelGenerator:

      def __init__(self):
            pass
      
      def generate(self, schema):
            pass

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
            fn.__name__ = "validate_%s"%(name)
            return fn

      def number_tests(self, schema):
            tests = self.numeric_tests(schema)
            tests.update({
                        "__isNumber" : (lambda value: isinstance(value, (int, long, float)), "'%(value)s' is not a number"),
                        })
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

