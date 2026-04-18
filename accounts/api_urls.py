
from django.urls import path
from . import api_views



urlpatterns = [
   
   
    path('api_login/', api_views.api_login, name='api_login'),
    path('set_session/', api_views.set_session, name='set_session'),
    path('get_session/', api_views.get_session, name='get_session'),
    path('cart/', api_views.cart_list_api,name='cart_list_api'),
    path('cart/update/', api_views.update_cart_quantity_api),
path('cart/clear/', api_views.clear_cart_api),
path('products/search/', api_views.product_search_api),
path('products/filter/', api_views.product_filter_api),
path('products/page/', api_views.product_pagination_api),
path('products/select-related/', api_views.products_select_related_api),
path('products/prefetch-related/', api_views.products_prefetch_related_api),
path('products/category/<int:id>/', api_views.products_by_category_api),
path('products/tag/<int:id>/', api_views.products_by_tag_api),
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
