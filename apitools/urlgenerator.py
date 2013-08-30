import re
import itertools

from .datagenerator import DataGenerator
from .schemasstore import SchemasStore

class UrlGenerator:

      args_regex = re.compile("\{([A-Z0-9\-_a-z]+)\}")

      def __init__(self):
            self.data_generator = DataGenerator()

      def generate_valid(self, schema):
            """Generate valid urls defined in the "links" section
               of the schema"""
            urls = {}
            for link in schema.get("links",[]):
                  urls[link["rel"]] = []
                  href = link["href"]

                  # for each argument, generate a list of valid values
                  # and store it in args
                  pos = 0
                  args = []
                  while True:
                        m = self.args_regex.search(href,pos) 
                        if not m:
                              break
                        # get the argument schema
                        arg_name = m.group(1)
                        arg_schema = schema["properties"][arg_name]
                        
                        # generate a list of valid values for the argument
                        args.append([self.data_generator.random_value(arg_schema)])
                        pos = m.end()+1

                  # replace stuff/{foo}/{bar} by stuff/%s/%s
                  href = re.sub(r"\{[a-zA-Z_]+\}",r"%s", href)

                  # generate a combinations of all the values and generate a url
                  # for each
                  combinations = itertools.product(*args)
                  for combination in combinations:
                        url = href%combination
                        urls[link["rel"]].append(url)
            return urls

if __name__ == "__main__":

      # load schemas
      store = SchemasStore()
      store.load_folder("data/schemas")
      
      # generate urls for the links in book
      generator = UrlGenerator()
      print(generator.generate_valid(store.schema("book",True)))

                        
                        
                  
                  
                  
                        
