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

jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

class MainHandler(webapp2.RequestHandler):
    def get(self):
        #template_values = {
        #    'name': 'SomeGuy',
        #    'verb': 'extremely enjoy'
        #}

        #template = jinja_environment.get_template('index.html')
        #self.response.out.write(template.render(template_values))

        self.redirect('/Rot13')

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
            

def escape_html(s):
        return cgi.escape(s,quote = True)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/Rot13',RotHandler)
], debug=True)
