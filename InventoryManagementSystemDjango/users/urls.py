from django.urls import path
from products.views import seller_products
from .views import Users, login

urlpatterns = [path('', Users.as_view(), name='sellers'),
               path("<int:id>", Users.as_view(), name='sellers'),
               path('login', login, name="login"),
               path("<int:id>/products", seller_products, name="seller_products"),
               ]
