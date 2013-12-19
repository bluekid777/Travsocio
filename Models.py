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
    username = db.StringProperty(required=True)
    current_lat = db.StringProperty()
    current_long = db.StringProperty()

    def __init__(self, id, name, username, current_lat='', current_long=''):
        self.id = id
        self.name = name
        self.current_lat = current_lat
        self.current_long = current_long
        self.username = username

    def get_current_location(self):
        if not self.current_lat == '':
            return self.current_lat, self.current_long
        else:
            return None

    def get_hometown(self):
        if not self.home_lat == '':
            return self.home_lat, self.home_long
        else:
            return None


class FacebookDataGraph (db.Model):
    def __init__(self, access_token):
        self.id = ''
        self.name = ''
        self.access_token = access_token
        self.friends = []
        self. places = []
        self.current_location_name = ''
        self.current_location_id = ''

    def create_facebook_graph(self):
        graph = facebook.GraphAPI(self.access_token)
        profile = graph.get_object("me")
        self.id = profile["id"]
        self.name = profile["name"]

        if profile.has_key("location"):
            loc = profile["location"]
            self.current_location_id = loc["id"]
            self.current_location_name = loc["name"]

        friends = graph.get_object("me/friends")
        friend_list = friends["data"]
        for friend in friend_list:

            detail = graph.get_object(friend["id"])

            if detail.has_key("username"):
                print "Gotcha"
                id = detail["id"]
                name = detail["name"]
                username = detail["username"]
                f = Friend(id=id, name=name, username=username, current_lat="", current_long="")
                self.friends.append(f)
                if len(self.friends) > 15:
                        break;
















