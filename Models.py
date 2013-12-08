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
    current_lat = db.StringProperty()
    current_long = db.StringProperty()
    home_lat = db.StringProperty()
    home_long = db.StringProperty()

    def __init__(self, id, name, current_lat='', current_long='', home_lat='', home_long=''):
        self.id = id
        self.name = name
        self.current_lat = current_lat
        self.current_long = current_long
        self.home_lat = home_lat
        self.home_long = home_long

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
            fid = friend["id"]
            fname = friend["name"]
            if friend.has_key("hometown"):
                home = friend["hometown"]
            else:
                home = ''
            if friend.has_key("location"):
                current = friend["location"]
            else:
                current = ""

            home_lat = ''
            home_long = ''
            current_lat = ''
            current_long = ''

            if not home == '':
                l = graph.get_object(home["id"])
                home_location = l["location"]
                home_lat = home_location["latitude"]
                home_long = home_location["longitude"]


            if not current == '':
                l = graph.get_object(current["id"])
                home_location = l["location"]
                current_lat = home_location["latitude"]
                current_long = home_location["longitude"]

            f = Friend(id=fid, name=fname, current_lat=current_lat, current_long=current_long, home_lat=home_lat, home_long=home_long)

            self.friends.append(f)
















