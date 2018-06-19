from .base import Session
from .models import User
from marshmallow import Schema

def getUser(email):
    Session.query(User).filter_by(email=email).first()
