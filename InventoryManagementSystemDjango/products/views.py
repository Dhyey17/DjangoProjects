from datetime import datetime

from core.utils import success_response, error_response, get_user_from_request
from django.core.files.storage import default_storage
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from users.models import Sellers

from .models import Products


# Create your views here.
class ProductListView(APIView):
    def get(self, request):
        try:
            products = Products.objects.filter(is_deleted=False)
            data = [{"id": p.id,
                     "name": p.name,
                     "seller_name": p.seller.name,
                     "price": p.price,
                     "quantity": p.quantity,
                     "expiry": p.expiry,
                     "image": p.image.url if p.image else None
                     } for p in products]

            return success_response(data={"products": data},
                                    msg="Products fetched successfully",
                                    status_code=status.HTTP_200_OK)

        except Exception:
            return error_response(msg="Internal Server Error",
                                  status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            seller, error = get_user_from_request(request)
            if error:
                return error

            name = request.data.get("name", "").strip()
            price = request.data.get("price", "").strip()
            quantity = request.data.get("quantity", "").strip()
            category = request.data.get("category", "").strip()
            expiry = request.data.get("expiry")
            image = request.FILES.get("image")

            if not name or not price or not quantity or not category:
                return error_response(msg="Name, price, quantity, and category are required",
                                      status_code=status.HTTP_400_BAD_REQUEST)

            try:
                price = float(price)
                quantity = int(quantity)
            except ValueError:
                return error_response(msg="Price and Quantity must be numbers",
                                      status_code=status.HTTP_400_BAD_REQUEST)

            expiry_date = None
            if expiry:
                try:
                    expiry_date = datetime.strptime(expiry, "%Y-%m-%d").date()
                except ValueError:
                    return error_response(msg="Expiry must be in YYYY-MM-DD format",
                                          status_code=status.HTTP_400_BAD_REQUEST)

            product = Products.objects.create(seller=seller, name=name, price=price, quantity=quantity,
                                              category=category, expiry=expiry_date, image=image)

            return success_response(data={"id": product.id,
                                          "name": product.name,
                                          "image": product.image.url if product.image else None},
                                    msg="Product created successfully",
                                    status_code=status.HTTP_201_CREATED)

        except Exception:
            return error_response(msg="Internal Server Error",
                                  status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductDetailView(APIView):
    def get(self, request, id):
        try:
            product = Products.objects.filter(id=id, is_deleted=False).first()
            if not product:
                return error_response(msg="Product not found",
                                      status_code=status.HTTP_404_NOT_FOUND)

            return success_response(data={"id": product.id,
                                          "name": product.name,
                                          "seller_name": product.seller.name,
                                          "price": product.price,
                                          "quantity": product.quantity,
                                          "expiry": product.expiry,
                                          "image": product.image.url if product.image else None},
                                    msg="Product fetched successfully",
                                    status_code=status.HTTP_200_OK)

        except Exception:
            return error_response(msg="Internal Server Error",
                                  status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, id):
        try:
            seller, error = get_user_from_request(request)
            if error:
                return error

            product = Products.objects.filter(id=id, is_deleted=False).first()
            if not product:
                return error_response(msg="Product not found",
                                      status_code=status.HTTP_404_NOT_FOUND)

            product.name = request.data.get("name", product.name)
            product.category = request.data.get("category", product.category)

            try:
                product.price = float(request.data.get("price", product.price))
                product.quantity = int(request.data.get("quantity", product.quantity))
            except ValueError:
                return error_response(msg="Price and Quantity must be numbers",
                                      status_code=status.HTTP_400_BAD_REQUEST)

            expiry = request.data.get("expiry")
            if expiry:
                try:
                    product.expiry = datetime.strptime(expiry, "%Y-%m-%d").date()
                except ValueError:
                    return error_response(msg="Expiry must be in YYYY-MM-DD format",
                                          status_code=status.HTTP_400_BAD_REQUEST)

            new_image = request.FILES.get("image")
            if new_image:
                if product.image and default_storage.exists(product.image.name):
                    default_storage.delete(product.image.name)
                product.image = new_image

            product.save()
            return success_response(data={"id": product.id,
                                          "name": product.name,
                                          "seller_name": product.seller.name,
                                          "price": product.price,
                                          "quantity": product.quantity,
                                          "expiry": product.expiry,
                                          "image": product.image.url if product.image else None},
                                    msg="Product updated successfully",
                                    status_code=status.HTTP_200_OK)

        except Exception:
            return error_response(msg="Internal Server Error",
                                  status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            seller, error = get_user_from_request(request)
            if error:
                return error

            product = Products.objects.filter(id=id, is_deleted=False).first()
            if not product:
                return error_response(msg="Product not found",
                                      status_code=status.HTTP_404_NOT_FOUND)
            product.delete()

            return success_response(msg="Product deleted successfully",
                                    status_code=status.HTTP_204_NO_CONTENT)

        except Exception:
            return error_response(msg="Internal Server Error",
                                  status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def seller_products(request, id):
    seller = Sellers.objects.filter(id=id, is_deleted=False).first()
    if not seller:
        return error_response(msg="Seller not found",
                              status_code=status.HTTP_404_NOT_FOUND)

    products = Products.objects.filter(seller=seller, is_deleted=False)
    data = [{"product_id": p.id,
             "name": p.name,
             "price": p.price,
             "quantity": p.quantity,
             "category": p.category,
             "image": p.image.url if p.image else None} for p in products]

    return success_response(data=data,
                            msg="Seller products fetched",
                            status_code=status.HTTP_200_OK)
