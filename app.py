import tornado.ioloop
import tornado.web
import tornado.log

import os
import boto3

client = boto3.client(
  'ses',
  region_name='us-east-1',
  aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
  aws_secret_access_key=os.environ.get('AWS_SECRET_KEY')
)

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
    
class PageHandler(TemplateHandler):
  def get(self, page):
    context = {}
    if page == 'form-success':
      context['message'] = "YAY!"
      
    page = page + '.html'
    self.set_header(
      'Cache-Control',
      'no-store, no-cache, must-revalidate, max-age=0')
    self.render_template(page, context)
    
def send_email (email, comments):
  response = client.send_email(
    Destination={
      'ToAddresses': ['robert.neelon@gmail.com']
    },
    Message={
      'Body': {
        'Text': {
          'Charset': 'UTF-8',
          'Data': '{} wants to talk to you\n\n{}'.format(email, comments),
        },
      },
      'Subject': {'Charset': 'UTF-8', 'Data': 'Test email'},
    },
    Source='robert.neelon@gmail.com',
  )

class SuccessHandler(TemplateHandler):
  def get(self):
    self.set_header(
      'Cache-Control',
      'no-store, no-cache, must-revalidate, max-age=0')
    self.render_template("form-success.html", {})
  
class FormHandler(TemplateHandler):
  def get(self):
    self.set_header(
      'Cache-Control',
      'no-store, no-cache, must-revalidate, max-age=0')
    self.render_template("form.html", {})
    
  def post(self):
      first_name = self.get_body_argument('first_name', None)
      last_name = self.get_body_argument('last_name', None)
      email = self.get_body_argument('email', None)
      comments = self.get_body_argument('comments', None)
      error = ''
      if email:
        print('EMAIL:', email)
        send_email(email, comments)
        self.redirect('/form-success')
        
      else:
        error = 'GIVE ME YOUR EMAIL!'
        
      self.set_header(
        'Cache-Control',
        'no-store, no-cache, must-revalidate, max-age=0')
      self.render_template("form.html", {'error': error})

class tempHandler(TemplateHandler):
  def get(self):
    self.set_header(
      'Cache-Control',
      'no-store, no-cache, must-revalidate, max-age=0')
    self.render_template("temp.html", {})
    
  def post(self):
      celsius = self.get_body_argument('celsius', None)
      celsius = float(celsius)
      tempF = celsius*1.8+32
      
        
      self.set_header(
        'Cache-Control',
        'no-store, no-cache, must-revalidate, max-age=0')
      self.render_template("temp.html", {'tempF': tempF})
    
    
def make_app():
  return tornado.web.Application([
    (r"/", MainHandler),
    (r"/form", FormHandler),
    (r"/temp", tempHandler),
    (r"/(form-success)", PageHandler),
    (r"/static/(.*)", tornado.web.StaticFileHandler, {'path': "static"})
  ], autoreload=True)
  
if __name__ == "__main__":
  tornado.log.enable_pretty_logging()
  
  app = make_app()
  PORT = int(os.environ.get('PORT', '8080'))
  app.listen(PORT)
  tornado.ioloop.IOLoop.current().start()