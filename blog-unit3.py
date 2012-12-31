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

import os
import webapp2
import jinja2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

class Post(db.Model):
    # numeric id created automatically by datastore
    title = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    content = db.TextProperty(required = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(Handler):
    def get(self):
        #posts = [ {"id": 111, "title": "my title", "date": "today", 
            #"content": "content goes here" } ]
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")
        self.render("blog-front.html", posts=posts)

class NewPost(Handler):
    def get(self):
        self.render("blog-newpost.html")

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if not subject or not content:
            error = "Subject and content, please"
            self.render("blog-newpost.html", subject=subject, content=content,
                            error=error)
        else:
            #self.render("blog-newpost.html", subject=subject, content=content)
            post = Post(title=subject, content=content)
            post.put()
            self.redirect("/blog/%s" % post.key().id())


class Permalink(Handler):
    def get(self, key_id):
        post = Post.get_by_id(int(key_id))
        self.render("blog-front.html", posts=[post])



app = webapp2.WSGIApplication([
                                ('/blog', MainPage),
                                ('/blog/newpost', NewPost),
                                ('/blog/([0-9]+)', Permalink),
                                ], debug=True)
