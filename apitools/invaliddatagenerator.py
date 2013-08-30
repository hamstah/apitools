#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import re
import string
from .datagenerator import DataGenerator

class InvalidDataGenerator:

      invalid_boolean_values = ["TRUE", "FALSE", "true ", "false ", 0, 1]
      invalid_integer_values = ["1.0", "0.0", "-0.9999999999999", "0.9999999999999", 
                                "1 ", " 34", "45 67", " 65 9 ", "45 str", "45str",
                                "str 5", "str5",
                                ]
      invalid_number_values = ["1.23 ", " 123.45", " 123.45 ", "123str.45"]
      invalid_non_string_values = [" ", "'", "&&", "||", "☃",">","</","<!--","*", ".", ""]

      invalid_strings = 10

      def __init__(self):
            self.data_generator = DataGenerator()

      def invalid_value(self, schema):
            if isinstance(schema, str):
                  schema = self.get_schema(schema)
            method = getattr(self, "invalid_%s"%schema["type"])
            
            return method(schema)

      def invalid_boolean(self, schema={}):
            return self.invalid_boolean_values +\
                self.invalid_integer_values +\
                self.invalid_number_values +\
                self.invalid_non_string_values

      def invalid_number(self, schema={}):

            invalids = self.invalid_non_string_values +\
                self.invalid_number_values + self.invalid_boolean_values

            if "minimum" in schema:
                  invalids.append(schema["minimum"] - 7)
                  if "exclusiveMinimum" in schema:
                        invalids.append(schema["minimum"])

            if "maximum" in schema:
                  invalids.append(schema["maximum"] + 7)
                  if "exclusiveMaximum" in schema:
                        invalids.append(schema["maximum"])         

            return invalids

      def invalid_integer(self, schema={}):
            invalids = self.invalid_number(schema) + self.invalid_integer_values
            
            if "divisibleBy" in schema:
                  invalids.append(schema["divisibleBy"]*7 + 4)
            
            return invalids


      def invalid_string(self, schema={}):
            invalids = []

            if "maxLength" in schema:
                  local_schema=dict(schema)
                  local_schema["maxLength"] = local_schema["minLength"] = schema["maxLength"]+1
                  invalids.append(self.data_generator.random_string(local_schema))

            if "minLength" in schema and schema["minLength"] > 0:
                  local_schema = dict(schema)
                  local_schema["minLength"] = local_schema["maxLength"] = schema["minLength"]-1
                  invalids.append(self.data_generator.random_string(local_schema))

            if "pattern" in schema:
                  pattern = schema["pattern"]

                  r_pattern = re.compile(pattern)
                  
                  if not r_pattern.match(""):
                        invalids.append("")

                  found=0
                  for i in range(100):
                        length = random.randint(0,100)
                        gen = ''.join(random.choice(string.printable) for x in range(length))

                        print(gen)
                        if gen not in invalids and not r_pattern.match(gen):

                              invalids.append(gen)
                              found += 1
                              if found == self.invalid_strings:
                                    break
            return invalids

            

if __name__ == "__main__":
      generator = InvalidDataGenerator()
      print(generator.invalid_number())
      print(generator.invalid_string({"pattern":"^[a-zA-Z]*$"}))

