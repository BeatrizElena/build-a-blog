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

# set up jinja. Use autoescape=True to escape html input by the user.
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    # function to call self.response.out.write, so I don't have to write that all the time.
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    # function takes a template name and returns a string of that rendered template
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    # function doesn't just return a string from the template, like the fx above,
    # it also calls self.write.
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

# Create entity (equivalent to table in sql)
# entities are created by creating a class.
# class inherits from db.Model()
# db.Model is included from google. We import it with: from google.appengine.ext import db
class Blog(db.Model):
    # 1st thing to do is define the type entities. (or the data types of the columns; in sql)
    title = db.StringProperty(required = True) # required=true sets a constrain for our db creation
    blog = db.TextProperty(required = True) # TextProperty allows for more characters that StringProperty
    created = db.DateTimeProperty(auto_now_add = True) # auto_now_add=true sets the time every time an instance of the entity is created.

class MainPage(Handler):
    def render_front(self, title="", blog="", error=""):
        # write the code, including the sql, to access the database.
        # This code creates a cursor "blogs" which is just a pointer to the results.
        blogs = db.GqlQuery("SELECT * FROM Blog " "ORDER BY created DESC ")
        # then we have to pass "blogs" to the front.html template in order to populate the page with the blogs
        self.render("front.html", title=title, blog=blog, error=error, blogs=blogs)

    # call render-front() fx with no parameters to render blank form.
    def get(self):
        # self.write('asciichan!') #writes asciichan! to the browser
        # self.render("front.html")  # renders the front.html file to the browser
        # call render_front() fx with no parameters to render blank form.
        self.render_front()

    # function to deal with form handling
    def post(self):
        # get parameters out of the request
        title = self.request.get("title")
        blog = self.request.get("blog")

        # add error handling code
        if title and blog:
            # initial response to see that initial form and error messages are working.
            self.write("thanks!")
            # create an instance of the Blog entity (i.e create an instance of the Blog table).
            # will call the instance b, and will only pass the title and blog parameters.
            # we don't pass the created parameter bc it's created automatically.
            a = Blog(title=title, blog=blog)
            # store b (the Blog object) in the database
            a.put()

            # to avoid the browser's reload message, create a redirect to within the same page,
            # below the submit boxes.
            self.redirect("/")
            # (we should see the title and art submitted below the submit boxes,
            # but only after adding space for it in our html form)



        else:
            error = "we need both a title and a blog entry!"
            # re-render the form, passing the error above into the form
            # self.render("front.html", error = error)
            # call render_front() fx with the error parameter to render form with error message.
            # include title and blog parameters bc we want to retain those inputs for the user
            # when we re-render the form.
            self.render_front(title, blog, error)

app = webapp2.WSGIApplication([
    ('/', MainPage)
], debug=True)
