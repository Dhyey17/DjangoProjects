from core.utils import (
    success_response,
    error_response,
    get_user_from_request,
    validate_order_type,
    validate_items,
    process_order_items
)
from django.db import transaction
from products.models import Products
from rest_framework import status
from rest_framework.views import APIView

from .models import Orders
from .serializers import OrderSerializer


class OrderView(APIView):
    def post(self, request):
        seller, error = get_user_from_request(request)
        if error:
            return error

        order_type = request.data.get("order_type")
        items = request.data.get("items")

        try:
            validate_order_type(order_type)
            validate_items(items)

            with transaction.atomic():
                order = Orders.objects.create(seller=seller, order_type=order_type)
                total_price = process_order_items(seller=seller, order=order, items=items)
                order.total_price = total_price
                order.save()
                serializer = OrderSerializer(order)

            return success_response(data=serializer.data,
                                    msg="Order created successfully",
                                    status_code=status.HTTP_201_CREATED)

        except ValueError as e:
            return error_response(msg=str(e),
                                  status_code=status.HTTP_400_BAD_REQUEST)

        except Products.DoesNotExist as e:
            return error_response(msg=str(e), status_code=status.HTTP_400_BAD_REQUEST)

        except Exception:
            return error_response(msg="Internal Server Error",
                                  status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, id=None):
        seller, error = get_user_from_request(request)
        if error:
            return error

        try:
            if id:
                order = Orders.objects.filter(id=id, seller=seller).first()
                if not order:
                    return error_response(msg="Order not found",
                                          status_code=status.HTTP_404_NOT_FOUND)

                serializer = OrderSerializer(order)
                return success_response(data=serializer.data,
                                        msg="Order fetched successfully",
                                        status_code=status.HTTP_200_OK)

            orders = Orders.objects.filter(seller=seller)
            serializer = OrderSerializer(orders, many=True)
            return success_response(data=serializer.data,
                                    msg="Orders fetched successfully",
                                    status_code=status.HTTP_200_OK)

        except Exception:
            return error_response(msg="Internal Server Error",
                                  status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
