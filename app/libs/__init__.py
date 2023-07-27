from app import bcrypt
from datetime import datetime as date_time
import calendar
import datetime
import time

def hashPassword(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

def hashdePassword(password,password_):
    return bcrypt.check_password_hash(password, password_)

# def timestamp():
#     # Timestamp
#     d = date_time.today()
#     return d


def timestamp():
    # Timestamp
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return timestamp

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def timeconverter(o):
    if isinstance(o, datetime.timedelta):
        return o.__str__()

def dateconvertor(o):
    if isinstance(o, datetime.date):
        return o.__str__()
