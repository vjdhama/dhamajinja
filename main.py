#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os, cgi
import webapp2
import jinja2
from google.appengine.ext import db

jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

class MainHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('base.html')
        self.response.out.write(template.render())

    def post(self):    
        r = self.request.get('rot').strip()
        a = self.request.get('ascii').strip()
        b = self.request.get('blog').strip()
        #self.response.out.write("r = " + r + "AND a = " + a)
        
        if r == 'GO':
            self.redirect('/rot13')
        elif a == 'GO':
            self.redirect('/ascii')
        elif b == 'GO':
            self.redirect('/blog')


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
        
    def render_str(self, template, **params):
        t = jinja_environment.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))
    
     
class RotHandler(Handler):
    def get(self):
        self.render('rot_form.html')

    def post(self):
        rot13 = ''
        text = self.request.get('text')
        if text:
            rot13 = text.encode('rot13')

        self.render('rot_form.html', text = rot13)

class SignupHandler(Handler):
    def get(self):
        self.render('signup.html')

class Art(db.Model):
    title = db.StringProperty(required = True)
    art = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class AsciiHandler(Handler):
    def render_front(self,title = "",art = "",error = ""):
        arts = db.GqlQuery("SELECT * FROM Art "
                           "ORDER BY created DESC")

        self.render("ascii.html", title = title, art = art, error = error, arts = arts)
    
    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        art = self.request.get("art")

        if art and title:
            a = Art(title = title , art = art)
            a.put()
            
            self.redirect("/ascii")
        else:
            error = "We need both title and art"
            self.render_front(title,art,error)


class BlogHandler(Handler):
    def render_blog(self,title = "",art = "",error = ""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC")

        self.render("blogs.html", blogs = blogs)
    
    def get(self):
        self.render_blog()

class Blog(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class PostHandler(Handler):
    def render_post(self,subject = "",content = "",error = ""):
        self.render("newpost.html", subject = subject, content = content, error = error)    

    def get(self):
        self.render_post()

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            b = Blog(subject = subject , content = content)
            b_key = b.put()
                        
            self.redirect("/blog/%d" %b_key.id())
        else:
            error = "We need both Subject and Content . . ."
            self.render_post(subject,content,error)

class SinglePost(webapp2.RequestHandler):
    def get(self, blog_id):
        s = Blog.get_by_id(int(blog_id))
        
        self.render("permalink.html", subject = s.subject ,  content = s.content, created = s.created)

def escape_html(s):
        return cgi.escape(s,quote = True)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/rot13', RotHandler),
    ('/signup', SignupHandler),
    ('/ascii',AsciiHandler),
    ('/blog',BlogHandler),
    ('/blog/newpost',PostHandler),
    ('/blog/([0-9]*)',SinglePost)
], debug=True)
