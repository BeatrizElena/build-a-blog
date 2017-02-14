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
import re
import string
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

# Create entity (i.e class)(equivalent to table in sql)
# class inherits from db.Model(), included with: from google.appengine.ext import db
class Blog(db.Model):
    # 1st thing to do is define the type entities. (or the data types of the columns; in sql)
    title = db.StringProperty(required = True) # required=true sets a constrain for our db creation
    blog = db.TextProperty(required = True) # TextProperty allows for more characters that StringProperty
    created = db.DateTimeProperty(auto_now_add = True) # auto_now_add=true sets the time every time an instance of the entity is created.
    # b = Blog(id, title=title, blog=blog)#???
    # b.put()
    # id = b.key().id()
    # id = Blog.get_by_id(id, parent=None)
# def entry_key(self, id):
#     id = int(self.request.get('id'))
#     blog = Blog.get(db.Key.from_path('entries', id))
#     return blog

class Index(Handler):
    def get(self, title="", blog=""):
        # t = jinja_env.get_template("frontpage.html")
        # content = t.render()
        # self.response.write(content)

        blogs = db.GqlQuery("SELECT * FROM Blog " "ORDER BY created DESC " "LIMIT 5")
        # then we have to pass "blogs" to the frontpage.html template in order to populate the page with the blogs
        self.render("frontpage.html", title=title, blog=blog, blogs=blogs)

class NewPost(Handler):
    def render_front(self, title="", blog="", error=""):
        # write the code, including the sql, to access the database.
        # This code creates a cursor "blogs" which is just a pointer to the results.
        blogs = db.GqlQuery("SELECT * FROM Blog " "ORDER BY created DESC " "LIMIT 5")
        # then we have to pass "blogs" to the frontpage.html template in order to populate the page with the blogs
        self.render("new-post.html", title=title, blog=blog, error=error, blogs=blogs)


    # call render-front() fx with no parameters to render blank form.
    def get(self):
        # call render_front() fx (with no parameters to render form blank)
        self.render_front()

    # function to deal with form handling
    def post(self):
        # get parameters out of the request
        title = self.request.get("title")
        blog = self.request.get("blog")

        # add error handling code
        if title and blog:
            # To have Cloud Datastore assign a numeric ID automatically, omit the key_name argument:
            # Create an entity with a key such as Employee:8261.
            # employee = Employee()
            # create an instance of the Blog entity (i.e create an instance of the Blog table).
            # blog_key = Blog(parent = entry_key(id), title=title, blog=blog)#???
            # # store b (the Blog object) in the database
            blog = Blog()
            blog.put()
            # # id = b.key().id()
            # # id = Blog.get_by_id(id, parent=None)
            # # id = b.key().id()
            # # b = Blog(id, title=title, blog=blog)#???
            # id = str(Blog.get_by_id(id, parent=None))
            # self.redirect("/blog?id=%s" % id)
            # blog = str(b.key().id())
            self.redirect('/blog/%s' % str(blog.key().id()))
            # self.redirect('/blog/%s' % id)
            # self.redirect('/')
            # self.response.write("I want to see a single blog!!")
            # self.redirect('/welcome?username=%s' % username)
        else:
            error = "We need both a title and a blog entry!"
            # re-render the form, passing the error above into the form
            # include title and blog parameters bc we want to retain those when we re-render the form.
            self.render_front(title, blog, error)

# class ViewPostHandler(Handler):
#     def get(self):
#         self.response.write("%s" % (Blog.key().id()), Blog.blog)
#
#     def post(self):
#         blog = Blog(blog=self.request.get('post'))
#         blog.put()
#         self.redirect('/')

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        if Entry.get_by_id(int(id)) == None:
            error = "No post associated with that ID."
            self.response.write(error)

       blog_id= Entry.get_by_id(int(id))
       self.response.write(blog_id.title)
       self.response.write(blog_id.entry)

    # def get(self, id):
    #     id = Blog.get_by_id(int(id))
        # if id:
        #     return id
        # self.response.write(id)
        # else:
            # error = "There are no blogs with the ID!"
            # self.response.write(error)

app = webapp2.WSGIApplication([
    ('/', Index),
    ('/newpost', NewPost),
    (webapp2.Route('/blog/<id:\d+>', ViewPostHandler))
], debug=True)

# class Comment(db.Model):
#     content = db.StringProperty(multiline=True)
#
# class MainPage(webapp2.RequestHandler):
#     def get(self):
#         self.response.write('<html><body><h1>Datastore Tutorial</h1>')
#         # self.query = Comment.all()
#         # for self.comment in self.query:
#         #     # print the id of the comment in bold.
#         #     # self.comment.key().id() gets the Key of the comment. Once we have the Key, we get the ID.
#         #     self.response.write('<p><b>%s</b></p>' % (self.comment.key().id(), self.comment.content)
#         self.response.write("""Enter your comment:
#         <form method="post">
#         <input type="textarea" name="post"></input>
#         <input type="submit"></input>
#         </form>""")
#         self.response.write('</body></html>')
#
#     def post(self):
#         self.response.write('<html><body><h1>Datastore Tutorial</h1>')
#         self.response.write('<p>You entered:</p><p><b>%s</b></p>' % (self.request.get('post'))
#         self.response.write("</body></html>")
#         # self.comment = Comment(content=self.request.get('post'))
#         # #write to datastore
#         # self.comment.put()
#         # self.redirect('/')
#
#
# app = webapp2.WSGIApplication([
#     ('/', MainPage)
# ], debug=True)



        # example of using get_by_id:
        # def get_non_deleted(cls, id):
        #     entity = cls.get_by_id(id)
        #     if entity and not entity.deleted:
        #         return entity

        # Model.get_by_id (ids, parent=None)
        # Retrieves the model instance (or instances) for the given numeric ID (or IDs).
        # Arguments
        # ids
        # A numeric entity ID, or a list of numeric IDs.
        # parent
        # The parent entity for the requested entities, as a model or key, or None (the default) if the requested entities do not have a parent.
        # Multiple entities requested by one call must all have the same parent.

        # create an instance of the Blog entity (i.e create an instance of the Blog table).
        # will call the instance b, and will only pass the title and blog parameters.
        # we don't pass the created parameter bc it's created automatically.
        # b = Blog(parent = blog_key(), title=title, blog=blog)#???
        # store b (the Blog object) in the database
        # b.put()
        # b = Blog(id, title=title, blog=blog)#???
        # # b.put()
        # id = b.key().id()
        # id = Blog.get_by_id(id, parent=None)
        # id = b.key().id()
        # id = Blog.get_by_id(id, parent=None)
        # self.redirect("/blog?id=%s" % id)
