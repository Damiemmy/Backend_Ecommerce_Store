from rest_framework import serializers
from .models import Product,Cart,CartItem,Profile
from django.contrib.auth import get_user_model

User=get_user_model()


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

# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile
from .serializers import NewCartItemSerializer  # if needed elsewhere

User = get_user_model()

class ProfileSerializer(serializers.ModelSerializer):
    # Expose user fields directly (writable)
    username    = serializers.CharField(source='user.username', read_only=True)
    email       = serializers.EmailField(source='user.email', required=False)
    first_name  = serializers.CharField(source='user.first_name', required=False, allow_blank=True)
    last_name   = serializers.CharField(source='user.last_name', required=False, allow_blank=True)
    city        = serializers.CharField(source='user.city', required=False, allow_blank=True)
    state       = serializers.CharField(source='user.state', required=False, allow_blank=True)
    address     = serializers.CharField(source='user.address', required=False, allow_blank=True)
    phone       = serializers.CharField(source='user.phone', required=False, allow_blank=True)

    # Keep your existing nested read-only block if you still want it in responses
    User_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Profile
        # You can include 'user' (id) if you still need it, otherwise omit
        fields = [
            'username',
            'email', 'first_name', 'last_name',
            'city', 'state', 'address', 'phone',
            'image',
            'User_info',
        ]

    def get_User_info(self, obj):
        """
        Keep this to preserve your old response shape. If you don’t need it,
        you can remove this method and the field from Meta.
        """
        user = obj.user
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "city": getattr(user, "city", None),
            "state": getattr(user, "state", None),
            "address": getattr(user, "address", None),
            "phone": getattr(user, "phone", None),
        }

    def update(self, instance, validated_data):
        """
        validated_data may contain a nested 'user' dict (from source='user.<field>')
        and top-level 'image'.
        """
        user_data = validated_data.pop('user', {})
        user = instance.user

        # Update user fields
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        # Update profile fields (e.g., image)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'city', 'state', 'address', 'phone', 'password', 'password2']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # 🔑 Hash the password
        user.save()
        return user
    