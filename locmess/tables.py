from pony.orm import *
from locmess import settings

db = Database()
db.bind(settings.DB_TYPE, settings.DB_FILE_NAME, create_db=True)

class User(db.Entity):
    username = Required(str, unique=True)
    password = Required(str)
    token = Optional('Token')

class Token(db.Entity):
    user = Required('User')
    token = Optional(str)


db.generate_mapping(create_tables=True)
