# Locmess Server

## User login

The login operation is the only time when you provide a `username:password`
pair, after that all of the operations performed on the server require a token
even the **logout** one, (for security reasons). To get a new token, simply
login again, all of the previous sessions will be re-generated, since the
token will be updated.

### Notes/Comments

* After first login, send the token with every operation you perform on the server
* In the project spec they talk about a `session id`, our session id is the token
* The token is a very simple one, since it's not the main goal of the project
