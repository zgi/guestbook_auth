#!/usr/bin/env python
import os
import jinja2
import webapp2
from models import Vnos
from google.appengine.api import users

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params, login)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            user = users.get_current_user()
            if user:
                logiran = True
                logout_url = users.create_logout_url('/')

                params = {"logiran": logiran, "logout_url": logout_url, "user": user}
                if users.is_current_user_admin():
                    params = {"logiran": logiran, "logout_url": logout_url, "user": user, 'admin': True}
            else:
                logiran = False
                login_url = users.create_login_url('/')
                params = {"logiran": logiran, "logout_url": login_url, "user": user}

            template = jinja_env.get_template(view_filename)
            self.response.out.write(template.render(params))
        else:
            user = users.get_current_user()
            if user:
                logiran = True
                logout_url = users.create_logout_url('/')
                auth = {"logiran": logiran, "logout_url": logout_url, "user": user, 'admin': False}
                if users.is_current_user_admin():
                    auth = {"logiran": logiran, "logout_url": logout_url, "user": user, 'admin': True}
            else:
                logiran = False
                login_url = users.create_login_url('/')
                auth = {"logiran": logiran, "logout_url": login_url, "user": user}
            params.update(auth)
            template = jinja_env.get_template(view_filename)
            self.response.out.write(template.render(params))

class MainHandler(BaseHandler):
    def get(self):
        return self.render_template("hello.html")

class HelloHandler(BaseHandler):
    def get(self):
        return self.render_template("hello.html")


class VnosHandler(BaseHandler):
    def get(self):
        return self.render_template("vnos.html")

    def post(self):
        ime = self.request.get("ime").replace('<script>', '').replace('</script>', '')
        priimek = self.request.get("priimek").replace('<script>', '').replace('</script>', '')

        if ime == '':
            ime = 'neznanec'
        if priimek == '':
            priimek = 'neznanec'

        user = users.get_current_user()
        email = user.email()
        sporocilo = self.request.get("sporocilo").replace('<script>', '').replace('</script>', '')

        data = Vnos(ime=ime, priimek=priimek, email=email, sporocilo=sporocilo)
        data.put()
        return self.render_template("vnos.html")   #redirect_to('domov')

class SeznamSporocilHandler(BaseHandler):
    def get(self):
        seznam = Vnos.query(Vnos.izbrisan == False).fetch()
        params = {'seznam': seznam}
        return self.render_template("seznam_sporocil.html", params=params)

class UrediSporociloHandler(BaseHandler):
    def post(self, sporocilo_id):
        vnos = self.request.get('sporocilo')
        sporocilo = Vnos.get_by_id(int(sporocilo_id))
        sporocilo.sporocilo = vnos
        sporocilo.put()
        return self.redirect_to('seznam-sporocil')

class IzbrisiSporociloHandler(BaseHandler):
    def post(self, sporocilo_id):
        sporocilo = Vnos.get_by_id(int(sporocilo_id))
        sporocilo.izbrisan = True
        sporocilo.put()
        return self.redirect_to("seznam-sporocil")

class IzbrisanaSporocilaHandler(BaseHandler):
    def get(self):
        seznam = Vnos.query(Vnos.izbrisan == True).fetch()
        params = {'seznam': seznam}
        return self.render_template("izbrisana_sporocila.html", params=params)

class ObnoviSporociloHandler(BaseHandler):
    def post(self, sporocilo_id):
        sporocilo = Vnos.get_by_id(int(sporocilo_id))
        sporocilo.izbrisan = False
        sporocilo.put()
        return self.redirect_to("izbrisana-sporocila")

class IzvleciSporociloHandler(BaseHandler):
    def get(self, sporocilo_id):
        sporocilo = Vnos.get_by_id(int(sporocilo_id)).sporocilo
        return self.write(sporocilo)

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler, name='domov'),
    webapp2.Route('/hello', HelloHandler, name='kuca'),
    webapp2.Route('/vnos', VnosHandler),
    webapp2.Route('/seznam-sporocil', SeznamSporocilHandler, name='seznam-sporocil'),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>/uredi', UrediSporociloHandler),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>', IzvleciSporociloHandler),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>/izbrisi', IzbrisiSporociloHandler),
    webapp2.Route('/izbrisana-sporocila', IzbrisanaSporocilaHandler, name='izbrisana-sporocila'),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>/obnovi', ObnoviSporociloHandler),
], debug=True)
