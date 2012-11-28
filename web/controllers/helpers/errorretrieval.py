#TODO: This is duplicated in models/User.py, organize this
import re
from web.controllers.helpers.common import add_dicts
from web.externals.bcrypt import bcrypt as bc
from web.models import User


_UNAMEP = r'^[A-Za-z0-9_-]{4,21}$'
uname = re.compile(_UNAMEP)

_UDOB = r'^(0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])[- /.](19|20)\d\d$'
udob = re.compile(_UDOB)



def valid_password( password):
    p = len(password)
    if not ( p >= 8 and p < 50):
        return False, {'error_password': 'Invalid password length'}
    return True, {}


def valid_passwords(password, confirmation):
    errors = {}
    state = True

    if not password or not confirmation:
        errors['error_password'] = "Enter both password and confirmation"
        errors['error_verify'] = 'Enter both password and confirmation'
        state = False
    if not valid_password(password)[0]:
        errors['error_password'] = "Enter a valid password."
        state = False
    if not valid_password(confirmation)[0]:
        errors['error_verify'] = "Enter a valid confirmation password."
        state = False
    if password and password and password != confirmation:
        state = False
        errors['error_match'] = "Passwords do not match."

    return state, errors


def valid_username(username):
    errors = {}
    state = True
    if not uname.match(username):
        errors['error_invalid_username'] = 'Invalid username'
        state = False
    return state, errors


def valid_email(email, user=None):
    #TODO: validate email format (regex?)
    e = User.query(User.email == email).get(projection=['username'])

    if e and not user:
        return False, {'error_email': 'Invalid email'}
    elif e and user:
        if e.username == user.username:
            return True, {}
        else:
            return False, {'error_email': 'Invalid email'}
    return True, {}

def valid(username, email, password, confirmation):
    #TODO: check confirmation password, implemented in valid_passwords
    _, u = valid_username(username)
    ue, _ = user_exists(username)
    _, p = valid_passwords(password, confirmation)
    _, e = valid_email(email)
    ux = {}
    if ue:
        ux = {'error_user_exists': 'Username taken'}
    errors = add_dicts(u, e, p, ux)
    if not errors:
        return True, {}

    return False, errors

def user_exists(username):
    error = {}
    user = User.query(User.username_norm == username.lower()).fetch(1, projection=['username', 'password'])
    if not user:
        error['error_user_exists'] = 'User does not exist'
        return False, error
    return True, user[0]

def check_password(user, password):
    error = {}
    if bc.hashpw(password, user.password) != user.password:
        error['error_password'] = 'Invalid password'
        return False, error

def valid_user_at_login(username, password):
    u, user = user_exists(username)
    if u:
        p, perr = check_password(user, password)
        if not p:
            return p, perr
    else:
        return u, user

    return True, {}

def get_login_errors(username, password):
    vp, p = valid_password(password)
    vu, u = valid_username(username)
    if vu and vp:
        _, e = valid_user_at_login(username, password)
    else:
        e = {}

    d =  add_dicts(p, u, e)
    return d

def check_valid_receiver(username):
    u, err = valid_username(username)
    if u:
        ue, uerr = user_exists(username)
        return ue, uerr
    return u, err
