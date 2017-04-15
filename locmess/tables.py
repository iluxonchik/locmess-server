from pony.orm import *
from locmess import settings
from datetime import datetime

db = Database()
db.bind(settings.DB_TYPE, settings.DB_FILE_NAME, create_db=True)

class User(db.Entity):
    username = Required(str, unique=True)
    password = Required(str)
    token = Optional(bytes)
    kvp = Optional(Json)
    locations = Set('Location')
    messages = Set('Message')

class Location(db.Entity):
    name = Required(str, unique=True)
    author = Required(User)
    is_gps = Required(bool)  # True: GPS; False: WiFi APs
    location = Required(Json)
    messages = Set('Message')

class Message(db.Entity):
    author = Required(User)
    title = Required(str)
    location = Required(Location)  # JSON with GPS coord or WiFi AP list
    text = Required(str)
    is_centralized = Required(bool)  # True: centralized; False: decentralized
    is_black_list = Required(bool)  # True: blacklist; False: whitelist
    valid_from = Required(datetime, default=datetime.now())
    valid_until = Required(datetime, default=datetime.max)
    time_posted = Required(datetime, default=datetime.now())
    properties = Required(Json)
    is_visible = Required(bool, default=True)


db.generate_mapping(create_tables=True)
