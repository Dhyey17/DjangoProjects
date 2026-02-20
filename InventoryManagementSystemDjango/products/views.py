from datetime import datetime

from core.utils import success_response, error_response, get_user_from_request
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from users.models import Sellers

from .models import Products


# Create your views here.
class ProductView(APIView):
    def post(self, request):
        print(request.data)
        try:
            seller, error = get_user_from_request(request)
            if error:
                return error

            name = request.data.get("name", "").strip()
            price = request.data.get("price", "").strip()
            quantity = request.data.get("quantity", "").strip()
            category = request.data.get("category", "").strip()
            expiry = request.data.get("expiry")
            image = request.FILES.get("image_url")

            if not name or not price or not quantity or not category:
                return error_response(msg="Name, price, quantity, and category are required",
                                      status_code=status.HTTP_400_BAD_REQUEST)

            try:
                price = float(price)
                quantity = int(quantity)
            except ValueError:
                return error_response(msg="Price and Quantity must be a numbers",
                                      status_code=status.HTTP_400_BAD_REQUEST)

            expiry_date = None
            if expiry:
                try:
                    expiry_date = datetime.strptime(expiry, "%Y-%m-%d").date()

                except ValueError:
                    return error_response(msg="Expiry must be in YYYY-MM-DD format",
                                          status_code=status.HTTP_400_BAD_REQUEST)

            product = Products.objects.create(seller=seller, name=name, price=price, quantity=quantity,
                                              category=category, expiry=expiry_date, image_url=image)

            return success_response(data={"id": product.id,
                                          "name": product.name},
                                    msg="Product created successfully",
                                    status_code=status.HTTP_201_CREATED)

        except Exception as e:
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
             "category": p.category
             } for p in products]

    return success_response(data=data,
                            msg="Seller products fetched",
                            status_code=status.HTTP_200_OK)
