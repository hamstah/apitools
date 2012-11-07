import random
import string

from schemasstore import SchemasStore

class DataGenerator:
    number_range = [-50,50]
    string_range = [7,15]
    array_range = [5,10]

    string_charset = string.ascii_letters + string.digits + ' '

    basic_types = ["string", "boolean", "number", "integer"]

    def __init__(self, schemas_store=None):
        self.schemas_store = schemas_store#

    def random_value(self, schema):
        if isinstance(schema, basestring):
            schema = self.get_schema(schema)
        method = getattr(self, "random_%s"%schema["type"])
        
        return method(schema)

    def get_schema(self, type_name):
        if type_name in self.basic_types:
            return {"type":type_name}
        if self.schemas_store:
            return self.schemas_store.schema(type_name, True)
        return None
    
    def random_number(self, schema={}):
        minimum = schema.get("minimum", self.number_range[0])
        maximum = schema.get("maximum", self.number_range[1])

        if minimum > maximum:
            maximum = minimum
        
        return random.uniform(minimum, maximum)

    def random_integer(self, schema={}):
        minimum = schema.get("minimum", self.number_range[0])
        maximum = schema.get("maximum", self.number_range[1])

        if minimum > maximum:
            maximum = minimum
        
        return random.randint(minimum, maximum)

    def random_boolean(self, schema={}):
        return bool(random.getrandbits(1))

    def random_string(self, schema={}):

        min_length = schema.get("minLength", self.string_range[0])
        max_length = schema.get("maxLength", self.string_range[1])

        if min_length > max_length:
            max_length = min_length
        
        length = random.randint(min_length, max_length)
        return ''.join(random.choice(self.string_charset) for x in range(length))


    def random_array(self, schema):
        items_type = schema["items"]["type"]
        items_schema = self.get_schema(items_type)
        if not items_schema:
            raise Exception("Don't know how to generate '%s'"%items_type)

        min_items = schema.get("minItems", self.array_range[0])
        max_items = schema.get("maxItems", self.array_range[1])

        count = random.randint(min_items, max_items)
        
        return [ self.random_value(items_schema) for x in range(count)]
    
    def random_object(self, schema):
        obj = {}

        for prop_name, prop_schema in schema.get("properties",[]).items():
            obj[prop_name] = self.random_value(prop_schema)
        return obj
    

if __name__ == "__main__":

    generator = DataGenerator()

    # Generates random instances of basic types
    for basic_type in generator.basic_types:
        print generator.random_value(basic_type)

    # Same with basic properties
    print generator.random_value({"type":"number", "minimum":50})
    print generator.random_value({"type":"string", "maxLength":20, "minLength":15})
    

    # Generates a random array of string
    print generator.random_value({"type":"array", "items": {"type":"string"}})

    store = SchemasStore()
    store.load_folder("data/schemas/")
    generator.schemas_store = store
    
    # Generate a random object defined in data/schemas/search_results.json
    print generator.random_value("search_results")

    # Generates an array of search_result
    print generator.random_value({"type":"array", "items":{"type":"search_result"}})
