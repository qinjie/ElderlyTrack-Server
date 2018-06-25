import base64
import datetime
from uuid import uuid4
import hashlib
import hmac
import os

import jwt
from chalice import UnauthorizedError

JWT_SECRET = b'\xf7\xb6k\xabP\xce\xc1\xaf\xad\x86\xcf\x84\x02\x80\xa0\xe0'


def get_jwt_token(data, password, salt, hashed_password, jwt_secret):
    if verify_password(password, salt, hashed_password):
        return gen_jwt_token(data, jwt_secret)
    raise UnauthorizedError('Invalid password')


def gen_jwt_token(data, jwt_secret):
    now = datetime.datetime.utcnow()
    unique_id = str(uuid4())
    payload = {
        'sub': data,
        'iat': now,
        'nbf': now,
        'jti': unique_id,
        # NOTE: We can also add 'exp' if we want tokens to expire.
    }
    token = jwt.encode(payload, jwt_secret, algorithm='HS256')
    return token.decode()


def get_authorized_user(current_request):
    data = current_request.context['authorizer']['principalId'].split(',')
    data = (data + 2 * [''])[:2]
    email = data[0]
    role = data[1]
    return {"email": email, "role": role}


def decode_jwt_token(token, jwt_secret):
    return jwt.decode(token, jwt_secret, algorithms=['HS256'])


def encode_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16)
    else:
        salt = base64.b64decode(salt)

    password = password.encode()
    rounds = 100000
    hashed = hashlib.pbkdf2_hmac('sha256', password, salt, rounds)
    return {
        'hash': 'sha256',
        'salt': base64.b64encode(salt),
        'rounds': rounds,
        'hashed': base64.b64encode(hashed).decode('utf-8'),
    }


def verify_password(password, salt, hashed_password):
    result = encode_password(password=password, salt=salt)
    input_password = result['hashed']
    print(input_password)
    print(hashed_password)
    if hmac.compare_digest(input_password, hashed_password):
        return True
    else:
        return False
