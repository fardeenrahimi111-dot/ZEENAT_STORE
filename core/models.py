from django.db import models

# Create your models here.
from django.db import models
class product(models.Model):
    
      name = models.CharField(max_length=100)
      price = models.DecimalField(max_digits=10, decimal_places=2)
      quantity = models.IntegerField()
      description = models.TextField(blank=True,null=True)
      image = models.ImageField(upload_to='product_images/', blank=True, null=True)

      def __str__(self):
        return self.name