import json

from modelgenerator import ModelGenerator

from jinja2 import Template

backbone_template = Template("""
var {{ model_name }}Model = Backbone.Model.extend({
    urlRoot: '{{ url_root }}',
    idAttribute: '{{ id_attribute }}'
});

var {{ model_name }}Collection = Backbone.Collection.extend({
    model : {{ model_name }}Model
});
""")

class BackboneModelGenerator(ModelGenerator):

      def __init__(self):
            ModelGenerator.__init__(self)

      def generate(self, schema):
            attribs = ModelGenerator.generate(self, schema)
            
            template_args = {
                  "model_name" : schema["name"].title(),
                  "url_root" : attribs["links"]["root"][0],
                  "id_attribute" : attribs["key_name"],
                  }

            return backbone_template.render(template_args)
            

if __name__ == "__main__":
      schema = json.loads(open("data/schemas/message.json").read())

      generator = BackboneModelGenerator()
      print generator.generate(schema)

      
