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
import re
import cgi
import random
import string
import hashlib
import hmac
import json


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

SECRET = "secret"
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

class User(db.Model):
    username = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)

class Post(db.Model):
    # numeric id created automatically by datastore
    title = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    content = db.TextProperty(required = True)

    def get_dict(self):
        post_fields =   { 
                        "title": self.title,
                        "content": self.content, 
                        "created": self.created.strftime("%a %b %d %H:%M:%S %Y")
                        }
        return post_fields

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt=make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (h, salt)

def valid_pw(name, pw, h):
    salt = h.split(',')[1]
    return h == make_pw_hash(name, pw, salt)

def valid_login_user_id(username, password):
    error = False
    if (not USER_RE.match(username) or not PASS_RE.match(password)):
        return None

    user = User.all().filter("username =", username).get()
    if (not user):
        return None

    if valid_pw(username, password, user.pw_hash):
        return str(user.key().id())
    else:
        return None


def make_user_cookie(user_id):
    hash = hmac.new(SECRET, user_id).hexdigest()
    return "%s|%s" % (user_id, hash)

def valid_user_cookie(user_id, cookie):
    return (cookie == make_user_cookie(user_id))

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
        posts = Post.all().order("-created")
        self.render("blog-front.html", posts=posts)

class MainPageJson(Handler):
    def get(self):
        posts = Post.all().order("-created")
        post_dicts = list()
        for p in posts:
            post_dicts.append(p.get_dict())
        self.response.headers.add_header('Content-Type', 'application/json')
        self.write(json.dumps(post_dicts))

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
            post = Post(title=subject, content=content)
            post.put()
            self.redirect("/blog/%s" % post.key().id())


class Permalink(Handler):
    def get(self, key_id):
        post = Post.get_by_id(int(key_id))
        self.render("blog-front.html", posts=[post])

class PermalinkJson(Handler):
    def get(self, key_id):
        post = Post.get_by_id(int(key_id))
        self.response.headers.add_header('Content-Type', 'application/json')
        self.write(json.dumps(post.get_dict()))

class RegisterPage(Handler):
    def get(self):
        self.render("blog-register.html")

    def post(self):
        username= self.request.get("username")
        password= self.request.get("password")
        verify= self.request.get("verify")
        email= self.request.get("email")

        username_error = ""
        password_error = ""
        verify_error = ""
        email_error = ""

        if not USER_RE.match(username):
            username_error = "That's not a valid username."
        elif User.all().filter("username =", username).count(limit=10) > 0:
            username_error = "Username already in use."

        if not PASS_RE.match(password):
            password_error = "That wasn't a valid password."
        elif password != verify:
            verify_error = "Your passwords didn't match."

        if email != "" and not EMAIL_RE.match(email):
            email_error = "That's not a valid email. "

        if (username_error or password_error or verify_error or email_error):
            self.render("blog-register.html",
                            username=cgi.escape(username), 
                            email=cgi.escape(email),
                            username_error=username_error,
                            password_error=password_error,
                            verify_error=verify_error,
                            email_error=email_error     
                            )
        else:
            hash = make_pw_hash(username, password)
            user = User(username=username, pw_hash=hash)
            user.put()
            user_id = str(user.key().id())
            cookie = make_user_cookie(user_id)
            self.response.headers.add_header('Set-Cookie', 
                                                'user_id=%s; Path=/' % cookie)
            self.redirect("/blog/welcome")

class LoginPage(Handler):
    def get(self):
        self.render("blog-login.html")

    def post(self):
        username= self.request.get("username")
        password= self.request.get("password")

        user_id = valid_login_user_id(username, password)

        if (user_id == None):
            self.render("blog-login.html",
                            username=cgi.escape(username), 
                            error="Invalid login.")
        else:
            cookie = make_user_cookie(user_id)
            self.response.headers.add_header('Set-Cookie', 
                                                'user_id=%s; Path=/' % cookie)
            self.redirect("/blog/welcome")

class LogoutPage(Handler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
        self.redirect("/blog/signup")

class WelcomePage(Handler):
    def get(self):
        cookie = self.request.cookies.get("user_id")
        # TODO: handle malformed cookie
        user_id = cookie.split("|",1)[0]
        if not valid_user_cookie(user_id, cookie):
            self.redirect("/blog/signup")
        else:
            username = user_id
            username = User.get_by_id(int(user_id)).username
            self.write("Welcome, %s" % username)


app = webapp2.WSGIApplication([
                                ('/blog\.json', MainPageJson),
                                ('/blog/\.json', MainPageJson),
                                ('/blog', MainPage),
                                ('/blog/newpost', NewPost),
                                ('/blog/([0-9]+)\.json', PermalinkJson),
                                ('/blog/([0-9]+)', Permalink),
                                ('/blog/signup', RegisterPage),
                                ('/blog/login', LoginPage),
                                ('/blog/welcome', WelcomePage),
                                ('/blog/logout', LogoutPage),
                                ], debug=True)
