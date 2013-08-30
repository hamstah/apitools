import json
import sys
import optparse

from jinja2 import Template

from .modelgenerator import ModelGenerator

html_template = Template("""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8"/>
    <title></title>
    <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.8.1/jquery.min.js"></script>
    <script type="text/javascript" src="http://ajax.cdnjs.com/ajax/libs/underscore.js/1.3.1/underscore-min.js"></script>
    <script type="text/javascript" src="http://ajax.cdnjs.com/ajax/libs/backbone.js/0.9.2/backbone-min.js"></script>
  </head>
  <body lang="en">
    <script type="text/javascript">
    {{ js }}
    </script>
  </body>
</html>
""")

js_template = Template("""
$(document).ready(function() {

    window.App = { Models : {}, Collections : {} };
{% for schema in schemas %}{{ schema }}
{% endfor %}
});
""")

backbone_template = Template("""
App.Models.{{ model_name }} = Backbone.Model.extend({
    urlRoot: '{{ url_root }}',
    idAttribute: '{{ id_attribute }}'
});

App.Collections.{{ model_name }}s = Backbone.Collection.extend({
    model : App.Models.{{ model_name }}{% if collection_url %},
    url : "{{ collection_url }}"{% else %}
    /* no "instances" link defined, fetch() won't work */{% endif %}
});
""")

class BackboneModelGenerator(ModelGenerator):

      def __init__(self):
            ModelGenerator.__init__(self)

      def generate(self, schemas, output_type="html"):
            if not output_type in ["js", "wrapped", "html" ]:
                  raise Exception("Invalid output type: %s"%output_type)

            def indent_block(text, num_spaces):
                  return "\n".join((num_spaces * " ") + i for i in text.splitlines())

            def generate_one(schema):
                  attribs = ModelGenerator.generate(self, schema)

                  template_args = {
                        "model_name" : schema["name"].title(),
                        "url_root" : attribs["links"]["root"][0],
                        "id_attribute" : attribs["key_name"],
                        "collection_url" : attribs["links"].get("instances",None)
                        }

                  return backbone_template.render(template_args)

            if isinstance(schemas, dict):
                  result = [generate_one(schemas)]
            else:
                  result = [generate_one(schema) for schema in schemas]
            
            
            if output_type == "js":
                  return "\n".join(result)

            js = js_template.render({"schemas":[indent_block(code, 4) for code in result]})
            if output_type == "wrapped":
                  return js

            return html_template.render({"js": indent_block(js,8)})

if __name__ == "__main__":
      parser = optparse.OptionParser(usage="usage: %prog jsonfile1 [jsonfile2]...")
      parser.add_option('-t', '--type', help='Output type (js|wrapped|html)', default="html", dest='output_type',action='store')
      (opts, args) = parser.parse_args()

      generator = BackboneModelGenerator()
      print(generator.generate([json.loads(open(f).read()) for f in args], opts.output_type))

      
