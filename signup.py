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
import webapp2
import cgi
import re
from string import Template

template = """
<!DOCTYPE html>

<html>
  <head>
    <title>Sign Up</title>
    <style type="text/css">
      .label {text-align: right}
      .error {color: red}
    </style>

  </head>

  <body>
    <h2>Signup</h2>
    <form method="post">
      <table>
        <tr>
          <td class="label">
            Username
          </td>
          <td>
            <input type="text" name="username" value="$username">
          </td>
          <td class="error">
           $username_error 
          </td>
        </tr>

        <tr>
          <td class="label">
            Password
          </td>
          <td>
            <input type="password" name="password" value="">
          </td>
          <td class="error">
           $password_error 
          </td>
        </tr>

        <tr>
          <td class="label">
            Verify Password
          </td>
          <td>
            <input type="password" name="verify" value="">
          </td>
          <td class="error">
           $verify_error 
          </td>
        </tr>

        <tr>
          <td class="label">
            Email (optional)
          </td>
          <td>
            <input type="text" name="email" value="$email">
          </td>
          <td class="error">
           $email_error 
          </td>
        </tr>
      </table>

      <input type="submit">
    </form>
  </body>

</html>"""

t = Template(template)

class MainHandler(webapp2.RequestHandler):
    def render(self, username="", email="", username_error="", 
                    password_error="", verify_error="", email_error=""):
        self.response.out.write(t.substitute(username=username, email=email, 
            username_error=username_error, password_error=password_error, 
            verify_error=verify_error, email_error=email_error))

    def get(self):
        self.render()

    def post(self):
        USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        PASS_RE = re.compile(r"^.{3,20}$")
        EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

        username_raw = self.request.get("username")
        password_raw = self.request.get("password")
        verify_raw = self.request.get("verify")
        email_raw = self.request.get("email")

        username_error = ""
        password_error = ""
        verify_error = ""
        email_error = ""

        if not USER_RE.match(username_raw):
            username_error = "That's not a valid username."

        if not PASS_RE.match(password_raw):
            password_error = "That wasn't a valid password."
        elif password_raw != verify_raw:
            verify_error = "Your passwords didn't match."

        if email_raw != "" and not EMAIL_RE.match(email_raw):
            email_error = "That's not a valid email. "

        if (username_error or password_error or verify_error or email_error):
            self.render(username=cgi.escape(username_raw), 
                            email=cgi.escape(email_raw),
                            username_error=username_error,
                            password_error=password_error,
                            verify_error=verify_error,
                            email_error=email_error     
                            )
        else:
            self.redirect("/unit2/signup/welcome?username=%s" % username_raw)

class WelcomeHandler(webapp2.RequestHandler):
    def get(self):
        username_raw = self.request.get("username")
        self.response.out.write("Welcome, %s!" % cgi.escape(username_raw))

app = webapp2.WSGIApplication([ 
                            ('/unit2/signup', MainHandler),
                            ('/unit2/signup/welcome', WelcomeHandler) ], 
                            debug=True)
