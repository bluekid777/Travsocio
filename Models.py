from google.appengine.ext import db
import facebook

class User(db.Model):
    id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    profile_url = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)
    city = db.StringProperty(required=True)

class Place(db.Model):
    id = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    summary = db.StringProperty()
    latitude = db.StringProperty(required=True)
    longitude = db.StringProperty(required=True)

    def get_location(self):
        return self.latitude, self.longitude

class Friend(db.Model):
    id = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    location_id = db.StringProperty()
    latitude = db.StringProperty()
    longitude = db.StringProperty()

    def __init__(self, id, name,location_id='', latitude='', longitude=''):
        self.id = id
        self.name = name
        self.location_id = location_id
        self.latitude = latitude
        self.longitude = longitude

    def get_location(self):
        if len(self.latitude) > 0:
            return self.latitude, self.longitude
        else:
            return None


class FacebookDataGraph:
    def __init__(self, access_token):
        self.id = ''
        self.name = ''
        self.access_token = access_token
        self.friends = []
        self. places = []


    def create_facebook_graph(self):
        graph = facebook.GraphAPI(self.access_token)
        profile = graph.get_object("me")
        self.id = profile["id"]
        self.name = profile["name"]


