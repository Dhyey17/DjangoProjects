from django.urls import path
from .views import login, UserListView, UserDetailView

urlpatterns = [
    path('', UserListView.as_view(), name='seller-list'),
    path("<int:id>", UserDetailView.as_view(), name='seller-detailed'),
    path('login', login, name="login"),
]
