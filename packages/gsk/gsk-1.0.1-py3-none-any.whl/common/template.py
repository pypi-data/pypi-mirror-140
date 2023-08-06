from jinja2 import Environment, FileSystemLoader
from yajanpy.settings import *

file_loader = FileSystemLoader(TEMPLATE_DIRECTORY)
env = Environment(loader=file_loader)

class HtmlTemplate:
    def __init__(self,filename="",context={}):
        self.filename = filename
        self.context = context
    def render(self,filename="",context={}):
        global env
        # print(env)
        if context!={}:
            self.context = context
        if filename !="":
            self.filename = filename

        if self.filename != "":
            template = env.get_template(self.filename)
            output = template.render(self.context)
        else:
            output = ""
        return output

def render(filename,context):
    html = HtmlTemplate()
    return html.render(filename,context)