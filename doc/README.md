# LocMess Server

# Installing

Required:
    * Python 3.x

Run the following command:
`pip install -r requirements.txt`

To run the server:
`python run.py`

The server will start on port 8081

## Endpoints

**User Related:**
* NEW_USER : '/new/user' {username, password} -> {}
* LOGIN : '/login' {username, password} -> {token}
* LOGOUT : '/logout' {username, token} ->

**Location Related:**

* NEW_LOCATION : '/new/location'  {username, token, name, is_gps, location_json } -> {}
* GET_LOCATION = '/get/location'  {username, token, name} -> {res, author, is_gps, location}
* GET_ALL_LOCATIONS = '/get/location/all'  {username, token} -> [res, author, is_gps, location}, ...]


**Message Related:**

* NEW_MESSAGE : '/new/message' {username, token, title, location_name, text, is_centralized, is_black_list, properties, valid_from?, valid_until?} -> {}
* GET_GPS_MESSAGES : '/get/message/gps' {username, token, curr_coord} -> {"messages":[{username, token, msg_id, title, location_name, text, is_centralized, is_black_list, properties, valid_from?, valid_until?}]}
* GET_SSID_MESSAGES : '/get/message/ssid' {username, token, curr_coord} -> {"messages":[{username, token, msg_id, title, location_name, text, is_centralized, is_black_list, properties, valid_from?, valid_until?}]}
* DELETE_MESSAGE = '/delete/message' # {username, token, msg_id} -> {}
* GET_MY_MESSAGES = '/get/message/my' # {username, token} -> [username, token, msg_id, title, location_name, text, is_centralized, is_black_list, properties, valid_from?, valid_until?, ...]

**Profile Related:**

* UPDATE_KEY : '/profile/key/update' # {username, token, key, value} -> {}
* DELETE_KEY : '/profile/key/delete' # {username, token, key, value} -> {}
* GET_KEY_VALUE_BIN : '/get/profile/keys' # {username, token} -> {key1: value, key2: value2, ...}

In the same directory as this file is located, you will find a .json file which you can import
into the [Advanced REST Client](https://chrome.google.com/webstore/detail/advanced-rest-client/hgmloofddffdnphfgcellkdfbfbjeloo). It will be updated as new things are added/changed in the server.

## User login

The login operation is the only time when you provide a `username:password`
pair, after that all of the operations performed on the server require a token
even the **logout** one, (for security reasons). To get a new token, simply
login again, all of the previous sessions will be re-generated, since the
token will be updated.

## Location

All locations are specified in JSON.

GPS Location Format:

```
{
    "latitude" : 123,
    "longitude": 456,
    "radius": 1992
}
```

SSID Location Format:

```
{
    "SSIDs": ["eduroam", "ElGato", "TheDocumentary", "MEO-WiFi"]
}
```

There is an attribute on the `Location` table that indicated whether the location
is a GPS one or an SSID one (`is_gps` boolean).

### Example requests

New Location:

```
{
    "username":"thegame", "token":"gAAAAABY4bKwzNXJrqgZlh7F3W_MvZMB62HJc2ujLU9D-mfmp8Z6kI6zSnvTlOo-sKM3NERFo5jdCWjUMwKBU_3oZ2Ysq1AthQ==",
    "name":"Dre's House",
    "is_gps": "True",
    "location_json": "{\"latitude\":123, \"longitude\":456, \"radius\":1992}"
}
```

Get Location:

(request)
```
{
    "username":"thegame", "token":"gAAAAABY4brfZfvacThtwbfZxUZvSlYbum31kL1ULCFdQhI5jrP8jY73wmBdTKSsH0WIKcPkbmz_i69gm-jY2YpvpgkGaA4wsw==",
    "name":"Dre's House"
}
```

(response)
```
{
  "name": "Dre's House",
  "author": "thegame",
  "is_gps": true,
  "location": "{\"latitude\":123, \"longitude\":456, \"radius\":1992}"
}
```

## Messages

### Creating A New Message

### Notes/Comments

* After first login, send the token with every operation you perform on the server
* In the project spec they talk about a `session id`, our session id is the token
* The token is a very simple one, since it's not the main goal of the project


* All requests are PUT
* 200 means OK, 401 means error
