from django.urls import path
from .views import OrderView

urlpatterns = [
    path("", OrderView.as_view(), name="orders"),
    path("<int:id>/", OrderView.as_view(), name="order_detail"),
]
