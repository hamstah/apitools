class ValidationException(Exception):
      
      def __init__(self, type_name, value, message):
            Exception.__init__(self, "%s is an invalid %s value: %s"%(value, type_name, message))

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
            found_tests = [item for item in tests.items() if item[0] in schema]
            if len(found_tests) == 0:
                  return None
            
            def fn(self, key, value):
                  for test_type, (test_fn, message) in found_tests:
                        test_value = schema[test_type]
                        if not test_fn(value,test_value):
                              raise ValidationException(name, value, message%{"test_type":test_type, 
                                                                              "test_value":test_value}) 
                  return value
            fn.__name__ = "validate_%s"%(name)
            return fn

      def number_tests(self, schema):
            return self.numeric_tests(schema)

      def integer_tests(self, schema):
            tests = self.numeric_tests(schema)
            
            tests.update({
                        "divisibleBy" : (lambda value, test_value : value%test_value == 0, "not divisible by %(test_value)s")
                        })
            return tests

      def numeric_tests(self, schema):
            message = "%(test_type)s is %(test_value)s"
            
            tests = {
                  "minimum": (lambda value,test_value: value >= test_value, message),
                  "maximum": (lambda value,test_value: value <= test_value, message),
                  "exclusiveMinimum" : (lambda value, test_value: value != schema["minimum"], message),
                  "exclusiveMaximum" : (lambda value, test_value: value != schema["maximum"], message),              
                  }    
            return tests

