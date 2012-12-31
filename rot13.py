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
from string import Template

form = """
<form method="post"> 
What is your birthday?<br>
<label>Month<input type="text" name="month"></label><br>
<label>Day<input type="text" name="day"></label><br>
<label>Year<input type="text" name="year"></label><br>
<input type="submit">
</form>
"""

template = """
<!DOCTYPE html>

<html>
  <head>
    <title>Unit 2 Rot 13</title>
  </head>

  <body>
    <h2>Enter some text to ROT13:</h2>
    <form method="post">
      <textarea name="text"
                style="height: 100px; width: 400px;">$text</textarea>
      <br>
      <input type="submit">
    </form>
  </body>

</html>
"""

t = Template(template)

def rot13_ch(ch):
    asc = ord(ch)
    if ( (asc >= ord("a") and asc < ord("a")+13)
            or (asc >= ord("A") and asc < ord("A")+13) ):
        return chr(asc+13)
    elif ( (asc >= ord("a")+13 and asc < ord("a")+26)
            or (asc >= ord("A")+13 and asc < ord("A")+26) ):
        return chr(asc-13)
    else:
        return ch

def rot13(text):
    return "".join(map(rot13_ch, text))


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(t.substitute(text=""))

    def post(self):
        text_raw = self.request.get("text")
        text_rot13 = rot13(text_raw)
        text_escape = cgi.escape(text_rot13)
        self.response.out.write(t.substitute(text=text_escape))

app = webapp2.WSGIApplication([ ('/unit2/rot13/', MainHandler)], debug=True)
