from django.db import models
from users.models import Sellers


# Create your models here.
class Products(models.Model):
    seller = models.ForeignKey(Sellers, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=120)
    price = models.FloatField()
    quantity = models.IntegerField()
    expiry = models.DateField(null=True)
    category = models.CharField(max_length=120)
    image_url = models.ImageField(upload_to='products', null=True)
    is_deleted = models.BooleanField(default=False)

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save()
