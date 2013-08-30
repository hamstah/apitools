import re


class ValidationError(Exception):
    def __init__(self, type_name, value, message):
        Exception.__init__(self, "'%s' is an invalid %s value: %s" % (
            value, type_name, message))


def number_tests(schema):
    tests = numeric_tests(schema)
    tests["__isNumber"] = (lambda value: isinstance(value, (
        int, float)), "'%(value)s' is not a number")
    return tests


def integer_tests(schema):
    tests = numeric_tests(schema)
    tests.update({
                "__isInt": (lambda value: isinstance(value, int), "'%(value)s' is not an integer"),
                "divisibleBy": (lambda value, div_by: value %div_by == 0, "not divisible by %(test_value)s")
                })
    return tests


def numeric_tests(schema):
    message = "%(test_type)s is %(test_value)s"

    tests = {
          "minimum": (lambda value, min_value: value >= min_value, message),
          "maximum": (lambda value, max_value: value <= max_value, message),
          "exclusiveMinimum": (lambda value, is_exclusive: not is_exclusive or value != schema["minimum"], message),
          "exclusiveMaximum": (lambda value, is_exclusive: not is_exclusive or value != schema["maximum"], message),
          }
    return tests


def string_tests(schema):
    tests = {
          "__isString": (lambda value: isinstance(value, basestring), "'%(value)s' is not a string"),
          "minLength": (lambda value, min_len: len(value) >= min_len, "length must be >= %(test_value)s"),
          "maxLength": (lambda value, max_len: len(value) <= max_len, "length must be <= %(test_value)s"),
          "pattern": (lambda value, pattern: re.match(pattern, value), "must match %(test_value)r"),
          }
    return tests


def generate_validator_from_tests(prop_name, schema, tests):
    """Combine test functions into a single validator"""
    # only keep the relevant tests
    found_tests = [(name, test) for (name, test) in list(tests.items())
                   if name in schema or name.startswith("__")]

    # if no tests are found, no validator is required
    if len(found_tests) == 0:
        return None

    def fn(self, key, value):
        for test_name, (test_fn, message) in sorted(found_tests,
                                                    key=lambda test: test[0]):
            res = False
            test_value = schema.get(test_name, None)
            if not test_name.startswith("__"):
                res = test_fn(value, test_value)
            else:
                res = test_fn(value)

            if not res:
                raise ValidationError(
                    prop_name, value, message % {"test_type": test_name,
                                                 "test_value": test_value,
                                                 "value": value})
        return value
    fn.__name__ = str("validate_%s" % (prop_name))
    return fn


def generate_validator_for_property(prop_name, schema):
    attr_name = "%s_tests" % schema["type"]
    method = globals().get(attr_name, None)

    if not method:
        return None
    tests = method(schema)

    if "enum" in schema:
        tests["enum"] = (
            lambda value, values: value in values,
            " % (value)s is not in the enum list")

    return generate_validator_from_tests(prop_name, schema, tests)
