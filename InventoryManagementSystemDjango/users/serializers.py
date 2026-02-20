from rest_framework import serializers
from .models import Sellers

class SellerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = Sellers
        fields = ["__all__"]
        extra_kwargs = {}
