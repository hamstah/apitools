import json
import os

class SchemasStore:

    def __init__(self):
        self.schemas = {}

    def add_schema(self, schema):
        try:
            if isinstance(schema, dict):
                j_schema = json.dumps(schema)
                self.schemas[schema["name"]] = (j_schema, schema)
            elif isinstance(schema, str):
                d_schema = json.loads(schema)
                self.schemas[d_schema["name"]] = (schema, d_schema)
            return True
        except:
            return False

    def schema(self, name, as_dict=False):
        if name not in self.schemas:
            return None

        if not as_dict:
            return self.schemas[name][0]
        return self.schemas[name][1]

    def load_folder(self, folder):
        """Loads schemas from a folder"""
        for name in os.listdir(folder):
            path = os.path.join(folder,name)
            if os.path.isfile(path):
                schema = open(path).read().replace("\t"," "*8)
                self.add_schema(schema)

                
                
