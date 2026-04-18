from django.urls import path
from . import views, api_views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view,name='logout'),
    path('dashboard/', views.dashboard,name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
   path('add-cart/<int:product_id>/', views.add_to_cart, name='add_cart'),
path('remove-cart/<int:product_id>/', views.remove_cart, name='remove_cart'),
path('cart/', views.cart_view, name='cart'),
path('products/', views.product_list,name='products'),
path('create-order/', api_views.create_order_api),
]
