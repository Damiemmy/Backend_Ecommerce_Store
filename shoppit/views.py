from django.shortcuts import render
from rest_framework.decorators import api_view
from .models import Product,Cart,CartItem,Transaction
from .serializers import ProductSerializer,DetailedProductSerializer,CartItemSerializer,SimpleCartSerializer,CartSerializer,UserSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from decimal import Decimal
import uuid
import requests
from rest_framework import status
import paypalrestsdk
from django.conf import settings

BASE_URL=settings.REACT_BASE_URL
paypalrestsdk.configure({
    "mode":settings.PAYPAL_MODE,
    "client_id":settings.PAYPAL_CLIENT_ID,
    "client_secret":settings.PAYPAL_CLIENT_SECRET
})

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
    return Response({"product_in_cart":exist_in_cart})

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

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def userinfo(request):
    user_info=request.user.username
    return Response({'username': user_info})


@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def UserBio(request):
    user_info=request.user
    serializer=UserSerializer(user_info)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    if request.user:
        try:
            #Generate a unique transaction refrence
            tx_ref=str(uuid.uuid4())
            cart_code=request.data.get('cart_code')
            cart=Cart.objects.get(cart_code=cart_code)
            user=request.user

            amount=sum([item.quantity*item.product.price for item in cart.items.all()])
            tax=Decimal("4.00")
            total_amount=amount+tax
            currency="NGN"
            redirect_url=f"{BASE_URL}/payment-status/"

            transaction=Transaction.objects.create(
                ref=tx_ref,
                cart=cart,
                user=user,
                amount=total_amount,
                currency=currency,
                status='pending'
            )
            flutterwave_payload={
                "tx_ref":tx_ref,
                "amount":str(total_amount),
                "currency":currency,
                "redirect_url":redirect_url,
                "customer":{
                    "email":user.email,
                    "name":user.username,
                    "phone_number":user.phone,
                },
                "customizations":{
                    "title":"Di-Felisha Payment"
                }

            }
            #set up the headers for the request
            headers={
                "Authorization":f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
                "Content-Type":"application/json"
            }

            #Make the Api request to flutterwave
            response=requests.post(
                "https://api.flutterwave.com/v3/payments",
                json=flutterwave_payload,
                headers=headers
            )
            if response.status_code==200:
                return Response(response.json(),status=status.HTTP_200_OK)
            else:
                return Response(response.json(),status=status.HTTP_200_OK)
        
        
        except requests.exceptions.RequestException as e:
            #log the error and return an erro response
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(['POST'])
def payment_callback(request):
    status=request.GET.get('status')
    tx_ref=request.GET.get('tx_ref')
    transaction_id=request.GET.get('transaction_id')

    user = request.user
    
    if status == 'successful':
        #Verify the transaction using Flutterwave's API
        headers={
            "Authorization":f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"
        }
        response =requests.get(f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify",headers=headers)
        response_data=response.json()

        if response_data['status']=='success':
            transaction=Transaction.objects.get(ref=tx_ref)

            #Confirm the transaction details
            if(response_data['data']['status']=="successful"
                    and float(response_data['data']['amount'])==float(transaction.amount)
                    and response_data['data']['currency']==transaction.currency):
                #Update transaction and cart status to paid
                transaction.status='completed'
                transaction.save()

                cart=transaction.cart
                cart.paid=True
                cart.user=user
                cart.save()
                
                return Response({'message':'Payment successfull!','subMessage':' you have successfully made payment to the items you Purchase🤩'})
            else:
                #Payment verification failed
                return Response({'message':'Payment verification failed.','subMessage':'your payment verification'})
        else:
            return Response({'message':'Failed to verify transaction with Flutterwave.','subMessage':'Error in transaction details'})
    else:
        return Response({'message':'Payment was not Successful.'},status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_paypal_payment(request):
    try:
        tx_ref = str(uuid.uuid4())
        user = request.user
        cart_code = request.data.get("cart_code")
        cart = Cart.objects.get(cart_code=cart_code)
        
        amount = sum(item.product.price * item.quantity for item in cart.items.all())
        tax = Decimal("4.00")
        total_amount = amount + tax

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": f"{BASE_URL}/payment-status?paymentStatus=success&ref={tx_ref}",
                "cancel_url": f"{BASE_URL}/payment-status?paymentStatus=cancel"
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": "Cart Items",
                        "sku": "cart",
                        "price": str(total_amount),
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": str(total_amount),
                    "currency": "USD"
                },
                "description": "Payment for cart items."
            }]
        })

        transaction, created = Transaction.objects.get_or_create(
            ref=tx_ref,
            cart=cart,
            amount=total_amount,
            user=user,
            status='pending'
        )

        if payment.create():
            for link in payment.links:
                if link.rel == "approval_url":
                    return Response({"approval_url": str(link.href)}, status=200)
            return Response({"error": "No approval URL found."}, status=500)
        else:
            print("PayPal error:", payment.error)
            return Response({"error": payment.error}, status=400)

    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def paypal_payment_callback(request):
    payment_id = request.query_params.get('paymentId')
    payer_id = request.query_params.get('PayerID')
    ref = request.query_params.get('ref')
    user = request.user

    if not all([payment_id, payer_id, ref]):
        return Response({"error": "Missing required parameters."}, status=400)

    try:
        transaction = Transaction.objects.get(ref=ref)
        payment = paypalrestsdk.Payment.find(payment_id)

        if payment.execute({"payer_id": payer_id}):
            transaction.status = 'completed'
            transaction.save()

            cart = transaction.cart
            cart.paid = True
            cart.user = user
            cart.save()

            return Response({"message": "Payment completed successfully."}, status=200)
        else:
            print("Execution error:", payment.error)
            return Response({"error": payment.error}, status=400)

    except Transaction.DoesNotExist:
        return Response({"error": "Transaction not found."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)




