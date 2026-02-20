from core.utils import success_response, error_response, generate_jwt, get_user_from_request
from django.contrib.auth.hashers import make_password, check_password
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView

from .models import Sellers


# Create your views here.
class UserDetailView(APIView):
    def get(self, request, id):
        seller = Sellers.objects.filter(id=id, is_deleted=False).first()
        if not seller:
            return error_response(msg="Seller not found",
                                  status_code=status.HTTP_404_NOT_FOUND)

        return success_response(data={"seller_id": seller.id,
                                      "seller_name": seller.name,
                                      "seller_username": seller.username},
                                msg="Seller fetched successfully",
                                status_code=status.HTTP_200_OK)

    def patch(self, request, id):
        seller_from_token, error = get_user_from_request(request)
        if error:
            return error

        if seller_from_token.id != id:
            return error_response(msg="Forbidden Access",
                                  status_code=status.HTTP_403_FORBIDDEN)

        seller = Sellers.objects.filter(id=id, is_deleted=False).first()
        if not seller:
            return error_response(msg="Seller not found",
                                  status_code=status.HTTP_404_NOT_FOUND)

        seller.name = request.data.get("name", seller.name)
        seller.username = request.data.get("username", seller.username)

        if request.data.get("password"):
            seller.password = make_password(request.data.get("password"))

        seller.save()
        return success_response(data={"seller_id": seller.id,
                                      "seller_name": seller.name,
                                      "seller_username": seller.username},
                                msg="Seller updated",
                                status_code=status.HTTP_200_OK)

    def delete(self, request, id):
        seller_from_token, error = get_user_from_request(request)
        if error:
            return error

        if seller_from_token.id != id:
            return error_response(msg="Forbidden Access",
                                  status_code=status.HTTP_403_FORBIDDEN)

        seller = Sellers.objects.filter(id=id, is_deleted=False).first()
        if not seller:
            return error_response(msg="Seller not found",
                                  status_code=status.HTTP_404_NOT_FOUND)

        seller.delete()

        return success_response(msg="Seller Deleted Successfully",
                                status_code=status.HTTP_204_NO_CONTENT)


class UserListView(APIView):
    def get(self, request):
        sellers = Sellers.objects.filter(is_deleted=False)
        data = [{"seller_id": s.id,
                 "seller_name": s.name,
                 "seller_username": s.username
                 } for s in sellers]
        return success_response(data=data,
                                msg="Sellers Fetched Successfully",
                                status_code=status.HTTP_200_OK)

    def post(self, request):
        name = request.data.get("name", "").strip()
        username = request.data.get("username", "").strip()
        password = request.data.get("password", "").strip()

        if not name or not username or not password:
            return error_response(msg="name, username and password are required",
                                  status_code=status.HTTP_400_BAD_REQUEST)

        if Sellers.objects.filter(username=username).exists():
            return error_response(msg="Username already exists",
                                  status_code=status.HTTP_409_CONFLICT)

        seller = Sellers.objects.create(name=name, username=username, password=make_password(password))
        return success_response(data={"seller_id": seller.id},
                                msg="Seller created",
                                status_code=status.HTTP_201_CREATED)


@api_view(["POST"])
def login(request):
    username = request.data.get("username", "").strip()
    password = request.data.get("password", "").strip()

    seller = Sellers.objects.filter(username=username, is_deleted=False).first()

    if not seller or not check_password(password, seller.password):
        return error_response(msg="Invalid credentials",
                              status_code=status.HTTP_401_UNAUTHORIZED)

    token = generate_jwt(seller.id)
    return success_response(data={"token": token},
                            msg="Login successful",
                            status_code=status.HTTP_200_OK)
