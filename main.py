#!/usr/bin/env python

FACEBOOK_APP_ID = '1426929370852106'
FACEBOOK_APP_SECRET = '2158fd034e3235b417de3e55bd6df0c9'
GOOGLE_API_KEY = 'AIzaSyAQhPtv1ef2PKLoYK9swqQEp-dBh7rIaHc'

import facebook
import webapp2
import os
import jinja2
import urllib2
import wikipedia
import logging
import urllib
import datetime

from Models import User
from webapp2_extras import sessions
from google.appengine.ext import db
from googleplaces import GooglePlaces, lang, types
from Models import Friend
from Models import FacebookDataGraph
from Models import Markers
from Models import Comment
from Models import Experience
from Models import Event

config = {}
config['webapp2_extras.sessions'] = dict(secret_key='')



class BaseHandler(webapp2.RequestHandler):


    @property
    def current_user(self):
        if self.session.get("user"):
            # User is logged in
            return self.session.get("user")
        else:
            # Either used just logged in or just saw the first page
            # We'll see here
            cookie = facebook.get_user_from_cookie(self.request.cookies,
                                                   FACEBOOK_APP_ID,
                                                   FACEBOOK_APP_SECRET)
            if cookie:
                # Okay so user logged in.
                # Now, check to see if existing user
                user = User.get_by_key_name(cookie["uid"])
                if not user:
                    # Not an existing user so get user info
                    graph = facebook.GraphAPI(cookie["access_token"])
                    profile = graph.get_object("me")
                    loc = profile["location"]
                    loc_id = loc["id"]
                    city = graph.get_object(loc_id)

                    user = User(
                        key_name=str(profile["id"]),
                        id=str(profile["id"]),
                        name=profile["name"],
                        profile_url=profile["link"],
                        access_token=cookie["access_token"],
                        city = city["name"]
                    )
                    print user.access_token
                    user.put()
                elif user.access_token != cookie["access_token"]:
                    user.access_token = cookie["access_token"]
                    user.put()
                # User is now logged in
                self.session["user"] = dict(
                    name=user.name,
                    profile_url=user.profile_url,
                    id=user.id,
                    access_token=user.access_token
                )
                return self.session.get("user")
        return None

    def dispatch(self):

        self.session_store = sessions.get_store(request=self.request)
        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):

        return self.session_store.get_session()


class HomeHandler(BaseHandler):
    def get(self):

        template = jinja_environment.get_template('dhome.html')


        # wiki api link: https://github.com/goldsmith/Wikipedia#
        # google image search api :: https://github.com/BirdAPI/Google-Search-API

        if self.session.get('city'):
            ny = wikipedia.page(self.session.get('city'))
        else:
            ny = wikipedia.page('Dresden')

        # google places api -- > https://github.com/slimkrazy/python-google-places
        cu = self.current_user

        if self.session.get('mark'):
            markers = self.session.get('mark')
        else:
            markers = ""

        friend_list = []

        if cu:
            f = FacebookDataGraph(cu["access_token"])
            f.create_facebook_graph()

            for fr in f.friends:
                try:
                    friend_list.append(dict(name=fr.name,
                                            id=fr.id,
                                            username=fr.username
                                            ))
                except:
                    print ""

        print friend_list
          #  print str(place.geo_location)

        self.response.out.write(template.render(dict(
            facebook_app_id=FACEBOOK_APP_ID,
            current_user=cu,
            summary=ny.summary,
            link=ny.url,
            markers=markers,
            friends=friend_list
        )))

    def post(self):
        url = self.request.get('url')
        file = urllib2.urlopen(url)
        graph = facebook.GraphAPI(self.current_user['access_token'])
        response = graph.put_photo(file, "Test Image")
        photo_url = ("http://www.facebook.com/"
                     "photo.php?fbid={0}".format(response['id']))
        self.redirect(str(photo_url))


class MobileHandler(BaseHandler):
    def get(self, params=""):
        template = jinja_environment.get_template('mhome.html')

        cu = self.current_user

        marker = self.session.get("mark")

        if self.session.get("friends"):
            friend_list = self.session.get("friends")
        else:
            friend_list = []

            if cu:
                f = FacebookDataGraph(cu["access_token"])
                f.create_facebook_graph()

                for fr in f.friends:
                    try:
                        friend_list.append(dict(name=fr.name,
                                                id=fr.id,
                                                username=fr.username
                        ))
                    except:
                        print ""
            self.session["friends"] = friend_list

        exp = db.GqlQuery("SELECT * FROM Experience")

        self.response.out.write(template.render(dict(
            facebook_app_id=FACEBOOK_APP_ID,
            current_user=cu,
            markers=marker,
            friends=friend_list,
            exp=exp
        )))


class WikiHandler(BaseHandler):
    def get(self):
        template = jinja_environment.get_template('wiki.html')

        if self.session.get("city"):
            wik = wikipedia.page(self.session.get("city"))
        else:
            wik = wikipedia.page("Dresden")

        summary = wik.summary
        link = wik.url
        title = wik.title
        self.response.out.write(template.render(dict(
            current_user=self.session.get("user"),
            title=title,
            summary=summary,
            link=link
        )))


class LocationHandler(BaseHandler):
    def get(self):
        template = jinja_environment.get_template('location_mobile_form.html')
        self.response.out.write(template.render(current_user=self.session.get("user")))

    def post(self):
        city = self.request.get('city')
        category = self.request.get('category')

        ##Image Search##


        google_places = GooglePlaces(GOOGLE_API_KEY)
        query_results = google_places.nearby_search(location=city, keyword=category, radius=20000)

        if query_results.has_attributions:
            print query_results.html_attributions

        locname = []
        loclat = []
        loclong = []
        marker = ""

        for place in query_results.places:
            try:
                n = str(place.name)
                location = place.geo_location
                lat = location["lat"]
                lng = location["lng"]
                locname.append(n)
                loclat.append(lat)
                loclong.append(lng)
            except:
                print " "

        for i in range(len(locname)):
            marker += locname[i]
            marker += ": "
            marker += str(loclat[i])
            marker += ", "
            marker += str(loclong[i])
            marker += "; "

        self.session["mark"] = marker
        self.session["city"] = city

        self.redirect('/')


class CommentHandler(BaseHandler):
    def get(self):
        template = jinja_environment.get_template('comment.html')

        if (self.session.get("user")):
            self.response.out.write(template.render(current_user=self.session.get("user"),
                                                    user=self.session.get("user")))

        else:
            self.response.out.write(template.render(user=None))

    def post(self):
        comment = self.request.get("comment")
        id = self.session.get("user")["id"]
        if self.session.get("city"):
            city = str(self.session.get("city")).lower()
        else:
            city = "dresden"
        co = Comment(name=city, uid=id, comment=comment)
        Comment.put(co)
        self.redirect('/mobile')


class EventHandler(BaseHandler):
    def get(self):
        template = jinja_environment.get_template('create_event.html')

        if (self.session.get("user")):
            self.response.out.write(template.render(current_user=self.session.get("user"),
                                                    user=self.session.get("user")))
        else:
            self.response.out.write(template.render(user=None))

    def post(self):
        starttime = str(self.request.get('startdate'))
        endtime = str(self.request.get('enddate'))
        name = self.request.get('event')
        print starttime
        print datetime.date.today()
        id = self.session.get('user')["id"]
        e = Event(name=name, uid=id, start=starttime, end=endtime)
        Event.put(e)
        self.redirect('/mobile')


class ExperienceHandler(BaseHandler):
    def get(self):
        template = jinja_environment.get_template('share_experience.html')

        if (self.session.get("user")):
            self.response.out.write(template.render(current_user=self.session.get("user"),
                                                    user=self.session.get("user")))

        else:
            self.response.out.write(template.render(user=None))

    def post(self):
        name = self.request.get("name")
        id = self.session.get("user")["id"]
        if self.session.get("city"):
            city = self.session.get("city")
        else:
            city = "Dresden"
        name = self.session.get("user")["name"]
        exp = self.request.get("story")

        ex = Experience(name=name, city=city, id=id, experience=exp)
        Experience.put(ex)

        graph = facebook.GraphAPI(self.current_user['access_token'])

        response = graph.put_wall_post(exp,profile_id="me")

        self.redirect('/mobile')


class MainHandler(BaseHandler):

    def get(self):
        user_agent_string = self.request.headers['user-agent']
        user_agent_string = user_agent_string.lower()
        if user_agent_string.find("mobile") >= 0:
            self.redirect('/mobile')
        else:
            self.redirect('/home')


class TodaysEventHandler(BaseHandler):
    def get(self):
        if self.session.get('user'):
            template = jinja_environment.get_template('todaysevents.html')
            events = db.GqlQuery('SELECT * FROM Event WHERE start = :1', str(datetime.date.today()))
            self.response.out.write(template.render(current_user=self.session.get("user"),
                                                    events=events))
        else:
            self.redirect('/mobile')

class LogoutHandler(BaseHandler):
    def get(self):
        if self.current_user is not None:
            self.session['user'] = None
            self.session["friends"] = None
            self.session["mark"] = None

        self.redirect('/')


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__))
)

app = webapp2.WSGIApplication(
    [('/', MainHandler), ('/mobile', MobileHandler), ('/home', HomeHandler), ('/logout', LogoutHandler),
     ('/location', LocationHandler), ('/wiki', WikiHandler), ('/comment', CommentHandler),
     ('/createevent', EventHandler), ('/shareex', ExperienceHandler),('/today', TodaysEventHandler)],
    debug=True,
    config=config
)