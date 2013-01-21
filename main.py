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
        r = self.request.get('rot')
        a = self.request.get('ascii')
        b = self.request.get('blog')
        #self.response.out.write("r = " + r + "AND a = " + a)
        
        if r == 'GO':
            self.redirect('/Rot13')
        elif a == 'GO':
            self.redirect('/Ascii')
        elif b == 'GO':
            self.redirect('/Blog')

        
class RotHandler(webapp2.RequestHandler):
    def write(self,arg = ""):
        template_values = {
            'data': arg,
         }
        template = jinja_environment.get_template('rot_form.html')
        self.response.out.write(template.render(template_values))
        
    def rot13(self,s):
        q = ''
        for a in s:
            if 123 > ord(a) > 96:
                if (ord(a) + 13) > 122:
                    q += chr(96 - 122 + (ord(a) + 13))
                else:
                    q += chr(ord(a) + 13)
            elif 91 > ord(a) > 64:
                if (ord(a) + 13) > 90:
                    q += chr(64 - 90 + (ord(a) + 13))
                else:
                    q += chr(ord(a) + 13)
            else:
                q += a
        return q
    
    def get(self):
        self.write()

    def post(self):
        d = self.request.get('t')
        if len(d) != 0:
            ans = self.rot13(d)
            self.write(ans)
        else:
            self.write()

class Art(db.Model):
    title = db.StringProperty(required = True)
    art = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class AsciiHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
        
    def render_str(self, template, **params):
        t = jinja_environment.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

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

            self.redirect("/Ascii")
            #self.render_front()
        else:
            error = "We need both title and art"
            self.render_front(title,art,error)


class BlogHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("Blog")


def escape_html(s):
        return cgi.escape(s,quote = True)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/Rot13',RotHandler),
    ('/Ascii',AsciiHandler),
    ('/Blog',BlogHandler)
], debug=True)
