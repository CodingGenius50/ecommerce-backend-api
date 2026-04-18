
from django.urls import path
from . import api_views



urlpatterns = [
   
   
    path('api_login/', api_views.api_login, name='api_login'),

 path('register/', api_views.register_api),
 
 
path('my-orders/', api_views.user_orders_api),
path('order/<int:order_id>/', api_views.order_details_api),
path('order/<int:order_id>/update-status/',api_views.update_order_status),
path('order/<int:order_id>/cancel/', api_views.cancel_order_api),
path('order/<int:order_id>/pay/', api_views.make_payment_api),
path('products/', api_views.product_list_api),
path('product/<int:product_id>/', api_views.product_detail_api),
path('product/create/', api_views.create_product_api),
path('cart/add/', api_views.add_to_cart_api),
]
