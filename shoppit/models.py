from django.db import models
from django.conf import settings
from django.utils.text import slugify


# Create your models here.
class Product(models.Model):
    CATEGORY=(
        ("ELECTRONICS","electronics"),
        ("SKINCARE","skincare"),
        ("CLOTHINGS","clothings"),
        ("FOR_MEN","for_men"),
        ("FOR_WOMEN","for women"),
    )
    name=models.CharField(max_length=100)
    image=models.ImageField(upload_to='img')
    description=models.TextField(blank=True,null=True)
    slug=models.SlugField(blank=True,null=True,max_length=15)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    category=models.CharField(max_length=15,choices=CATEGORY,blank=True,null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1
            while Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

class Cart(models.Model):
    cart_code=models.CharField(max_length=11,unique=True)
    user=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True,blank=True)
    paid=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True, null=True,blank=True)
    modified_at=models.DateTimeField(auto_now=True, null=True,blank=True)

    def __str__(self):
        return self.cart_code

class CartItem(models.Model):
    cart=models.ForeignKey(Cart,related_name='items',on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in cart{self.cart.id}"

