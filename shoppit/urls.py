from django.urls import path
from . import views

urlpatterns = [
    path('products/',views.products,name='products'),
    path('related_Products/<slug:slug>/',views.related_Products,name='related_Products'),
    path('additem/',views.additem,name='additem'),
    path('get_cart_stat/',views.get_cart_stat,name='get_cart_stat'),
    path('in_cart/',views.in_cart,name='in_cart'),
    path('Fetch_in_cart/',views.Fetch_in_cart,name='Fetch_in_cart'),
    path('Update_cart/',views.Update_cart,name='Update_cart'),
    path('Delete_item/',views.Delete_item,name='Delete_item'),
    
]
