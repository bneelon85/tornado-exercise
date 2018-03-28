import tornado.ioloop
import tornado.web
import tornado.log

import os

from jinja2 import \
  Environment, PackageLoader, select_autoescape
  
ENV = Environment(
  loader=PackageLoader('myapp', 'templates'),
  autoescape=select_autoescape(['html', 'xml'])
)

class TemplateHandler(tornado.web.RequestHandler):
  def render_template (self, tpl, context):
    template = ENV.get_template(tpl)
    self.write(template.render(**context))
    
class MainHandler(TemplateHandler):
  def get(self):
    self.set_header(
      'Cache-Control',
      'no-store, no-cache, must-revalidate, max-age=0')
    self.render_template("hello.html", {})
    
class FormHandler(TemplateHandler):
  def post(self):
    self.set_header(
      'Cache-Control',
      'no-store, no-cache, must-revalidate, max-age=0')
    self.render_template("form.html", {})
    
def make_app():
  return tornado.web.Application([
    (r"/", MainHandler),
  ], autoreload=True)
  
if __name__ == "__main__":
  tornado.log.enable_pretty_logging()
  
  app = make_app()
  PORT = int(os.environ.get('PORT', '8080'))
  app.listen(PORT)
  tornado.ioloop.IOLoop.current().start()