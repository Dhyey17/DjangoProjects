import datetime

import jwt
from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from users.models import Sellers
from orders.models import OrderItems
from products.models import Products


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

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token


def decode_jwt(token):
    try:
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
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
    seller = Sellers.objects.filter(id=user_id, is_deleted=False).first()

    if not seller:
        return (None, error_response(msg="Invalid user",
                                     status_code=status.HTTP_401_UNAUTHORIZED))

    return (seller, None)


def get_product_for_seller(product_id, seller):
    product = Products.objects.filter(id=product_id, seller=seller, is_deleted=False).first()
    if not product:
        raise ValidationError("Product not found")

    return product


def validate_order_type(order_type):
    if order_type not in ["INCOMING", "OUTGOING"]:
        raise ValidationError("Order type must be INCOMING or OUTGOING.")


def validate_items(items):
    if not items or not isinstance(items, list):
        raise ValidationError("Items must be a non-empty list.")

    for item in items:
        if "product_id" not in item:
            raise ValidationError("Each item must contain product_id.")

        if "quantity" not in item:
            raise ValidationError("Each item must contain quantity.")

        if not isinstance(item["quantity"], int) or item["quantity"] <= 0:
            raise ValidationError("Quantity must be a positive integer.")


def process_order_items(seller, order, items):
    total_price = 0
    for item in items:
        product = get_product_for_seller(product_id=item["product_id"],
                                         seller=seller)

        quantity = item["quantity"]
        price_at_time = product.price

        if order.type == "OUTGOING":
            if product.quantity < quantity:
                raise ValidationError(f"Insufficient stock for product {product.name}.")
            product.quantity -= quantity

        elif order.type == "INCOMING":
            product.quantity += quantity

        else:
            raise ValidationError(f"Order type {order.type} is not supported.")

        product.save()
        order_item = OrderItems.objects.create(order=order,
                                               product=product,
                                               quantity=quantity,
                                               price_at_time=price_at_time)
        total_price += order_item.total
    return total_price
