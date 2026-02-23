from django.core.files.storage import default_storage
from rest_framework import status
from rest_framework.views import APIView

from .models import Products
from core.utils import success_response, error_response, get_user_from_request, validate_product_fields, parse_expiry, \
    get_product_for_seller


# Create your views here.
class ProductListView(APIView):
    def get(self, request):
        seller, error = get_user_from_request(request)
        if error:
            return error

        try:
            products = Products.objects.filter(seller=seller, is_deleted=False)
            data = [{"id": p.id,
                     "name": p.name,
                     "price": p.price,
                     "quantity": p.quantity,
                     "category": p.category,
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
        seller, error = get_user_from_request(request)
        if error:
            return error

        try:
            parsed = validate_product_fields(request.data)

            expiry = request.data.get("expiry")
            if expiry:
                parsed["expiry"] = parse_expiry(expiry)

            image = request.FILES.get("image")

            product = Products.objects.create(seller=seller, image=image, **parsed)
            return success_response(data={"id": product.id},
                                    msg="Product created successfully",
                                    status_code=status.HTTP_201_CREATED)

        except ValueError as e:
            return error_response(msg=str(e),
                                  status_code=status.HTTP_400_BAD_REQUEST)

        except Exception:
            return error_response(msg="Internal Server Error",
                                  status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductDetailView(APIView):
    def get(self, request, id):
        seller, error = get_user_from_request(request)
        if error:
            return error

        try:
            product = get_product_for_seller(id, seller)
            return success_response(
                data={"id": product.id,
                      "name": product.name,
                      "price": product.price,
                      "quantity": product.quantity,
                      "category": product.category,
                      "expiry": product.expiry,
                      "image": product.image.url if product.image else None
                      },
                msg="Product fetched successfully",
                status_code=status.HTTP_200_OK)

        except Products.DoesNotExist:
            return error_response("Product not found", status.HTTP_404_NOT_FOUND)

    def patch(self, request, id):
        seller, error = get_user_from_request(request)
        if error:
            return error

        try:
            product = get_product_for_seller(id, seller)
            parsed = validate_product_fields(request.data, partial=True)
            expiry = request.data.get("expiry")
            if expiry:
                parsed["expiry"] = parse_expiry(expiry)

            for key, value in parsed.items():
                setattr(product, key, value)

            new_image = request.FILES.get("image")
            if new_image:
                if product.image and default_storage.exists(product.image.name):
                    default_storage.delete(product.image.name)
                product.image = new_image

            product.save()

            return success_response(msg="Product updated successfully",
                                    status_code=status.HTTP_200_OK)

        except ValueError as e:
            return error_response(msg=str(e),
                                  status_code=status.HTTP_400_BAD_REQUEST)

        except Products.DoesNotExist:
            return error_response(msg="Product not found",
                                  status_code=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id):
        seller, error = get_user_from_request(request)
        if error:
            return error

        try:
            product = get_product_for_seller(id, seller)
            product.delete()

            return success_response(msg="Product deleted successfully",
                                    status_code=status.HTTP_204_NO_CONTENT)

        except Products.DoesNotExist:
            return error_response(msg="Product not found",
                                  status_code=status.HTTP_404_NOT_FOUND)
