

import os
import jwt
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash

SECRET = os.getenv('JWT_SECRET_KEY')

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET, algorithm='HS256')

def verify_password(plain_pw, hashed_pw):
    return check_password_hash(hashed_pw, plain_pw)