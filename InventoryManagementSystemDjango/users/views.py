from django.contrib.auth.hashers import make_password, check_password
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView

from .models import Sellers
from core.utils import success_response, error_response, generate_jwt, get_user_from_request


# Create your views here.
class UserListView(APIView):
    def post(self, request):
        try:
            name = request.data.get("name", "").strip()
            username = request.data.get("username", "").strip()
            password = request.data.get("password", "").strip()

            if not name or not username or not password:
                raise ValueError("name, username and password are required")

            if Sellers.objects.filter(username=username).exists():
                return error_response(msg="Username already exists",
                                      status_code=status.HTTP_409_CONFLICT)

            seller = Sellers.objects.create(name=name,
                                            username=username,
                                            password=make_password(password))

            return success_response(data={"seller_id": seller.id},
                                    msg="Seller created successfully",
                                    status_code=status.HTTP_201_CREATED)

        except ValueError as e:
            return error_response(msg=str(e),
                                  status_code=status.HTTP_400_BAD_REQUEST)

        except Exception:
            return error_response(msg="Internal Server Error",
                                  status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserDetailView(APIView):
    def get(self, request, id):
        seller, error = get_user_from_request(request)
        if error:
            return error

        try:
            if seller.id != id:
                return error_response(msg="Forbidden Access",
                                      status_code=status.HTTP_403_FORBIDDEN)

            return success_response(data={"seller_id": seller.id,
                                          "seller_name": seller.name,
                                          "seller_username": seller.username
                                          },
                                    msg="Seller fetched successfully",
                                    status_code=status.HTTP_200_OK)

        except Exception:
            return error_response(msg="Internal Server Error",
                                  status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, id):
        seller, error = get_user_from_request(request)
        if error:
            return error

        try:
            if seller.id != id:
                return error_response(msg="Forbidden Access",
                                      status_code=status.HTTP_403_FORBIDDEN)

            name = request.data.get("name")
            username = request.data.get("username")
            password = request.data.get("password")

            if name:
                seller.name = name.strip()

            if username:
                username = username.strip()
                if Sellers.objects.filter(username=username).exclude(id=id).exists():
                    return error_response(msg="Username already exists",
                                          status_code=status.HTTP_409_CONFLICT)

                seller.username = username

            if password:
                seller.password = make_password(password.strip())

            seller.save()

            return success_response(msg="Seller updated successfully",
                                    status_code=status.HTTP_200_OK)

        except ValueError as e:
            return error_response(msg=str(e),
                                  status_code=status.HTTP_400_BAD_REQUEST)

        except Exception:
            return error_response(msg="Internal Server Error",
                                  status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        seller, error = get_user_from_request(request)
        if error:
            return error

        try:
            if seller.id != id:
                return error_response(msg="Forbidden Access",
                                      status_code=status.HTTP_403_FORBIDDEN)

            seller.delete()

            return success_response(msg="Seller deleted successfully",
                                    status_code=status.HTTP_204_NO_CONTENT)

        except Exception:
            return error_response(msg="Internal Server Error",
                                  status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def login(request):
    try:
        username = request.data.get("username", "").strip()
        password = request.data.get("password", "").strip()

        if not username or not password:
            raise ValueError("Username and password are required")

        seller = Sellers.objects.filter(username=username, is_deleted=False).first()

        if not seller or not check_password(password, seller.password):
            return error_response(msg="Invalid credentials",
                                  status_code=status.HTTP_401_UNAUTHORIZED)

        token = generate_jwt(seller.id)
        return success_response(data={"token": token},
                                msg="Login successful",
                                status_code=status.HTTP_200_OK)

    except ValueError as e:
        return error_response(msg=str(e),
                              status_code=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return error_response(msg="Internal Server Error",
                              status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
