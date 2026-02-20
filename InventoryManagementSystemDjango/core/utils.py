import datetime

import jwt
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status


def success_response(data=None, msg="", status_code=200):
    return Response({"success": True,
                     "msg": msg,
                     "data": data},
                    status=status_code)


def error_response(msg="", status_code=400):
    return Response({"success": False,
                     "msg": msg},
                    status=status_code)


def generate_jwt(user_id, expiry_minutes=30):
    payload = {"user_ID": user_id,
               "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=expiry_minutes)
               }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token


def decode_jwt(token):
    try:
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithm="HS256")
        return (decoded, None)

    except jwt.ExpiredSignatureError:
        return (None, "Token expired")

    except jwt.InvalidTokenError:
        return (None, "Invalid token")


def get_user_from_request(request):
    auth_head = request.headers.get("Authorization")
    if not auth_head:
        return (None, error_response(msg="Authorization header missing",
                                     status_code=status.HTTP_401_UNAUTHORIZED))

    parts = auth_head.split()
    if len(parts) != 2:
        return None, error_response(msg="Invalid Authorization header format",
                                    status_code=status.HTTP_401_UNAUTHORIZED)

    scheme, token = parts
    if scheme.lower() != "bearer":
        return None, error_response(msg="Authorization header must start with Bearer",
                                    status_code=status.HTTP_401_UNAUTHORIZED)
    decoded, error = decode_jwt(token)

    if error:
        return (None, error_response(msg=error,
                                     status_code=status.HTTP_401_UNAUTHORIZED))

    user_id = decoded.get("user_ID")
    seller = Sellers.objects.filter(id=user_id,
                                    is_deleted=False).first()

    if not seller:
        return (None, error_response(msg="Invalid user",
                                     status_code=status.HTTP_401_UNAUTHORIZED))

    return (seller, None)
