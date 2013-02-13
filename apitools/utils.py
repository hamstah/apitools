import re


url_args_regex = re.compile("\{([A-Z0-9\-_a-z]+)\}")

# TODO: cleanup that
def extract_re_matches(pattern, string):
    res = []
    pos = 0
    
    while True:
        m = pattern.search(string,pos) 
        if not m:
            break
        pos = m.end()+1
        res.append(m.group(1))
    return res

def get_url_args(url):
    return extract_re_matches(url_args_regex, url)

def get_resource_key(schema):
    
    if not "links" in schema:
        raise Exception("Missing links in schema")

    for link in schema["links"]:
        if link["rel"] == "self":
            args = get_url_args(link["href"])
            if len(args) == 0:
                raise Exception("No argument in the self link")
            if len(args) != 1:
                raise Exception("No unique argument in self link")
            return args[0]

    raise Exception("No self link in schema")
    

def url_to_flask_route(url, model):
    args = get_url_args(url)

    # transform the link url into a flask route
    for arg_name in args:
        arg_schema = model.properties[arg_name]
        flask_type = {"integer":"int",
                      "number":"float",
                      "string":"string"
                      }[arg_schema["type"]]
        url=url.replace("{%s}"%arg_name, "<%s:%s>"%(flask_type, arg_name))
    return url

def url_to_template(url):
    return re.sub(r"\{([a-zA-Z_]+)\}",r"%(\1)s", url)
