from rest_framework import serializers
from .models import Product,Cart,CartItem
from django.contrib.auth import get_user_model

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields=["id","name","slug","price","category","description","image"]

class DetailedProductSerializer(serializers.ModelSerializer):
    related_Products=serializers.SerializerMethodField()
    class Meta:
        model=Product
        fields=["id","name","slug","price","category","description","image","related_Products"]
    def get_related_Products(self,product):
        product=Product.objects.filter(category=product.category).exclude(id=product.id)
        serializer=ProductSerializer(product,many=True)
        return(serializer.data)

class CartItemSerializer(serializers.ModelSerializer):
    product=ProductSerializer(read_only=True)
    total=serializers.SerializerMethodField()
    class Meta:
        model=CartItem
        fields=['product','id','quantity','total']
    def get_total(self,cart):
        total=cart.product.price * cart.quantity
        return total



class CartSerializer(serializers.ModelSerializer):
    items=CartItemSerializer(read_only=True,many=True)
    sum_total=serializers.SerializerMethodField()
    class Meta:
        model=Cart
        fields=['id','created_at','modified_at','cart_code','items','sum_total']
    def get_sum_total(self,cart):
        item=cart.items.all()
        sum_total=sum([items.product.price * items.quantity for items in item])
        return sum_total
 
class SimpleCartSerializer(serializers.ModelSerializer):
    number_of_items=serializers.SerializerMethodField()
    sum_total=serializers.SerializerMethodField()
    class Meta:
        model=Cart
        fields=["id","cart_code","number_of_items","sum_total"]

    def get_number_of_items(self,carts):
        no_of_items=sum([item.quantity for item in carts.items.all()])
        return no_of_items
    def get_sum_total(self,cart):
        item=cart.items.all()
        sum_total=sum([items.product.price * items.quantity for items in item])
        return sum_total

class NewCartItemSerializer(serializers.ModelSerializer):
    product=ProductSerializer(read_only=True)
    order_id=serializers.SerializerMethodField()
    order_date=serializers.SerializerMethodField()
    class Meta:
        model=CartItem
        fields=["id","product","quantity","order_id","order_date"]
    def get_order_id(self,cartitem):
        order_id=cartitem.cart.cart_code
        return order_id
    
    def get_order_date(self,cartitem):
        order_date=cartitem.cart.modified_at
        return order_date

class UserSerializer(serializers.ModelSerializer):
    items=serializers.SerializerMethodField()
    class Meta:
        model=get_user_model()
        fields=['id','username','email','first_name','items','last_name','city','state','address','phone']

    def get_items(self,user):
        cartitems=CartItem.objects.filter(cart__user=user,cart__paid=True)[:10]
        serializer=NewCartItemSerializer(cartitems,many=True)
        return serializer.data 


