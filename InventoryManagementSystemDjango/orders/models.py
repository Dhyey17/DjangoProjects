from django.db import models
from products.models import Products
from users.models import Sellers


# Create your models here.
class Orders(models.Model):
    ORDER_TYPE_CHOICES = (
        ("INCOMING", "Incoming"),
        ("OUTGOING", "Outgoing"))

    seller = models.ForeignKey(Sellers, on_delete=models.CASCADE, related_name="orders")
    type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES)
    total_price = models.FloatField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)


class OrderItems(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price_at_time = models.FloatField()
    total = models.FloatField(editable=False)

    def save(self, *args, **kwargs):
        self.total = self.price_at_time * self.quantity
        super().save(*args, **kwargs)
