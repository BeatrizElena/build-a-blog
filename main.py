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
class Blog(db.Model):
    # 1st thing to do is define the type entities. (or the data types of the columns; in sql)
    title = db.StringProperty(required = True)
    blog = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class Index(Handler):
    def get(self, title="", blog=""):
        blogs = db.GqlQuery("SELECT * FROM Blog " "ORDER BY created DESC " "LIMIT 5")
        # pass "blogs" to the frontpage.html template in order to populate the page with the blogs
        self.render("frontpage.html", title=title, blog=blog, blogs=blogs)

class NewPost(Handler):
    def render_front(self, title="", blog="", error=""):
        # Access the db. This code creates a cursor "blogs" which is just a pointer to the results.
        blogs = db.GqlQuery("SELECT * FROM Blog " "ORDER BY created DESC " "LIMIT 5")
        # pass "blogs" to the frontpage.html template in order to populate the page with the blogs
        self.render("new-post.html", title=title, blog=blog, error=error, blogs=blogs)

    # call render-front() fx with no parameters to render blank form.
    def get(self):
        self.render_front()
    # function to deal with form handling
    def post(self):
        # get parameters out of the request
        title = self.request.get("title")
        blog = self.request.get("blog")

        # add error handling code
        if title and blog:
            # create an instance of the Blog entity (i.e create an instance of the Blog table).
            # will call the instance blog, and will only pass the title and blog parameters.
            blog = Blog(title=title, blog=blog)
            # store b (the Blog object) in the database
            blog.put()
            # id = Blog.get_by_id(int(id))
            # self.redirect("/")
            self.redirect('/blog/%s' % str(blog.key().id()))

        else:
            error = "We need both a title and a blog entry!"
            # re-render the form, passing the error above, the title and the blog content into the form
            self.render_front(title, blog, error)

class ViewPostHandler(Handler):
    def get(self, id):
        if Blog.get_by_id(int(id)) == None:
            error = "No blog entry associated with that ID."
            self.response.write(error)

        else:
            blog_id= Blog.get_by_id(int(id))
            self.response.write(blog_id.title)
            self.response.write("<div></div>")
            self.response.write(blog_id.blog)



app = webapp2.WSGIApplication([
    ('/', Index),
    ('/newpost', NewPost),
    (webapp2.Route('/blog/<id:\d+>', ViewPostHandler))
], debug=True)
