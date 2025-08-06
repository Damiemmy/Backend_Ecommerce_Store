from django.shortcuts import render
from rest_framework.decorators import api_view
from .models import Product,Cart,CartItem
from .serializers import ProductSerializer,DetailedProductSerializer,CartItemSerializer,SimpleCartSerializer,CartSerializer
from rest_framework.response import Response

# Create your views here.
@api_view(['GET'])
def products(request):
    product=Product.objects.all()
    serializer=ProductSerializer(product,many=True)
    return Response(serializer.data)

@api_view(['GET'])
def related_Products(request,slug):
    product=Product.objects.get(slug=slug)
    serializer=DetailedProductSerializer(product)
    return Response(serializer.data)

@api_view(['POST'])
def additem(request):
    try:
        cart_code=request.data.get('cart_code')
        product_id=request.data.get('product_id')

        cart,create=Cart.objects.get_or_create(cart_code=cart_code)
        product=Product.objects.get(id=product_id)

        cartitem,create=CartItem.objects.get_or_create(cart=cart,product=product)
        cartitem.quantity=1
        cartitem.save()
        serializer=CartItemSerializer(cartitem)
        return Response({"data":serializer.data,"message":"items added to cart successfully"},status=201)
    except Exception as e:
        return Response({"error":str(e)},status=400)

@api_view(['GET'])
def get_cart_stat(request):
    cart_code=request.query_params.get('cart_code')
    cart=Cart.objects.get(cart_code=cart_code,paid=False)
    serializer=SimpleCartSerializer(cart)
    return Response(serializer.data)

@api_view(['GET'])
def in_cart(request):
    cart_code=request.query_params.get('cart_code')
    product_id=request.query_params.get('product_id')

    cart=Cart.objects.get(cart_code=cart_code)
    product=Product.objects.get(id=product_id)

    exist_in_cart=CartItem.objects.filter(cart=cart,product=product).exists()
    exist_in_cart_shoppage=CartItem.filter(cart=cart,product=product)
    serializer=ProductSerializer(exist_in_cart_shoppage)
    return Response({"product_in_cart":exist_in_cart,"data":serializer.data})

@api_view(['GET'])    
def Fetch_in_cart(request):
    cart_code=request.query_params.get('cart_code')
    cart=Cart.objects.get(cart_code=cart_code,paid=False)
   
    serializer=CartSerializer(cart)
    return Response(serializer.data)

@api_view(['PATCH'])
def Update_cart(request):
    try:
        product_id=request.data.get('product_id')
        quantities=request.data.get('quantities')
        quantities=int(quantities)

        cartitems=CartItem.objects.get(id=product_id)

        cartitems.quantity=quantities
        cartitems.save()
        serializer=CartItemSerializer(cartitems)
        return Response({'data':serializer.data,'message':'cart updated successfully'},status=201)
    except Exception as e:
        return Response({'error':str(e)},status=400)

@api_view(['POST'])
def Delete_item(request):
    try:
        item_id=request.data.get('item_id')
        cartitem=CartItem.objects.get(id=item_id)
        delete_item=cartitem.delete()
        serializer=CartItemSerializer(delete_item)
        return Response({'message':"cartitem deleted successfully"},status=201)
    except Exception as e:
        return Response({'error':str(e)},status=400)




    

