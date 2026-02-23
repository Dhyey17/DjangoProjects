from rest_framework import serializers

from .models import Orders, OrderItems


class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    price_at_time = serializers.IntegerField(source="product.price", read_only=True)

    class Meta:
        model = OrderItems
        fields = [
            "id",
            "product_id",
            "product_name",
            "quantity",
            "price_at_time",
            "total"
        ]
        read_only_fields = ["id", "price_at_time", "total"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Orders
        fields = [
            "id",
            "order_type",
            "total_price",
            "timestamp",
            "items"
        ]
        read_only_fields = ["id", "total_price", "timestamp"]
