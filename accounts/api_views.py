from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from .cart_utils import get_or_create_cart

from rest_framework.response import Response
from rest_framework import status

from .models import Cart,CartItem,OrderItem,Order,Product
from .serializers import ProductSerializer,RegisterSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order_api(request):

    cart = get_or_create_cart(request)
    cart_items = CartItem.objects.filter(cart=cart)

    if not cart_items.exists():
        return Response({'error': 'Cart is empty'}, status=400)

    # ✅ Order create
    order = Order.objects.create(
        user=request.user
    )

    total_price = 0

    # 🔥 LOOP START
    for item in cart_items:
        product = item.product

        # ✅ 1. stock check
        if item.quantity > product.stock:
            return Response({
                "error": f"{product.name} out of stock"
            }, status=400)

        # ✅ 2. stock reduce
        product.stock -= item.quantity
        product.save()

        # ✅ 3. order item create
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item.quantity
        )

        total_price += product.price * item.quantity
    # 🔥 LOOP END

    # ✅ cart empty
    cart_items.delete()

    return Response({
        'message': 'Order created successfully',
        'order_id': order.id,
        'total_price': total_price
    })




    
    
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_orders_api(request):

    orders=Order.objects.filter(user=request.user)
    data=[]
    for order in orders:
        total_price=0
        for item in order.items.all():
            total_price+=item.product.price*item.quantity
        data.append({
            'order_id':order.id,
            'total_price':total_price,
            'status':order.status,
            'created_at':order.created_at,
            "is_paid": order.is_paid,
        })
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_details_api(request,order_id):
    
    try:
        order=Order.objects.get(id=order_id,user=request.user)
    except Order.DoesNotExist:
        return Response({'error':'Order not found'},status=404)
    items=order.items.all()
    data=[]
    for item in items:
        data.append({
            'product':item.product.name,
            'price':item.product.price,
            'quantity':item.quantity
            
        })
        
    return Response({
        'order_id':order_id,
        'status':order.status,
        'items':data,
        "is_paid": order.is_paid,
    })
    
from rest_framework.permissions import IsAdminUser

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_order_status(request,order_id):

    try:
        order=Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error':'Order not found'},status=404)
    new_status=request.data.get('status')

    if new_status not in['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
        return Response({'error': "Invalid status"},status=400)
    order.status=new_status
    order.save()
    return Response({
        'message':"Order status updated",
        'new_status':order.status
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def cancel_order_api(request,order_id):
    
    try:
        order=Order.objects.get(id=order_id,user=request.user)
    except Order.DoesNotExist:
        return Response({'error':'Order not found'}, status=404)
    
    if order.status in ['pending','processing']:
        order.status='cancelled'
        order.save()
        return Response({'message':"order cancelled successfully"})
    return Response({"error": "cannot cancel this order"},status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_payment_api(request, order_id):
    try: 
        order=Order.objects.get(id=order_id,user=request.user)
    except Order.DoesNotExist:
        return Response({"error":"order not found"}, status=404)
    
    if order.is_paid:
        return Response({"error":"already paid you order"},status=400)
    
    order.is_paid=True
    order.status='processing'
    order.save()
    
    return Response({
        'message':"payment successful",
        'order_id':order.id,
        "is_paid":order.is_paid,
        "status":order.status
        
    })
    
@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_product_api(request):
    
    name=request.data.get('name')
    description=request.data.get('description')
    price=request.data.get('price')
    stock=request.data.get("stock")
    text=request.data.get('text')
    
    product=Product.objects.create(
        name=name,
        description=description,
        price=price,
        stock=stock,
        text=text
    )  
    
    return Response({"message":"product created",
                    'product_id':product.id})
  
@api_view(['GET'])
def product_list_api(request):

    products = Product.objects.all()

    # search
    search = request.GET.get('search')
    if search:
        products = products.filter(name__icontains=search)

    # filter
    min_price = request.GET.get('min')
    max_price = request.GET.get('max')

    if min_price:
        products = products.filter(price__gte=int(min_price))

    if max_price:
        products = products.filter(price__lte=int(max_price))

    # pagination
    page = int(request.GET.get('page', 1))
    limit = 5
    start = (page - 1) * limit
    end = start + limit

    total = products.count()
    products = products[start:end]

    # 🔥 serializer use
    serializer = ProductSerializer(products, many=True)

    return Response({
        "page": page,
        "total": total,
        "results": serializer.data
    })
  
    

    
@api_view(['GET'])
def product_detail_api(request, product_id):

    try:
        p = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)

    return Response({
        "id": p.id,
        "name": p.name,
        "description":p.description,
        "price":p.price,
        "stock":p.stock,
        "text":p.text
    })    



    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart_api(request):

    product_id = request.data.get('product_id')
    quantity = int(request.data.get('quantity', 1))

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)

    # ✅ stock check
    if product.stock <= 0:
        return Response({"error": "Product out of stock"}, status=400)

    if quantity > product.stock:
        return Response({"error": "Not enough stock"}, status=400)

    cart = get_or_create_cart(request)

    # ✅ FIXED LOGIC
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity

    cart_item.save()

    return Response({
        "message": "Product added to cart"
    })
    
    
    
    
# =========================
# Product List + Create API
# =========================

# =========================
# API Login (Token Generate)
# =========================
@api_view(['POST'])
@permission_classes([AllowAny])   # 🔴 খুব গুরুত্বপূর্ণ
def api_login(request):

    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user is None:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    token, created = Token.objects.get_or_create(user=user)

    return Response({
        'token': token.key,
        'username': user.username
    })

# =========================
# Session SET API
# =========================
@api_view(['GET'])
def set_session(request):

    request.session['username'] = 'Hakim'
    request.session['role'] = 'student'

    return Response({'message': 'Session data set successfully'})

# =========================
# Session GET API
# =========================
@api_view(['GET'])
def get_session(request):

    username = request.session.get('username')
    role = request.session.get('role')

    return Response({
        'username': username,
        'role': role
    })
    




from .models import CartItem
from .serializers import CartItemSerializer
from .cart_utils import get_or_create_cart


# =========================
# CART VIEW API
# =========================
@api_view (['GET'])
@permission_classes ([AllowAny])
def cart_list_api(request):
    
    cart = get_or_create_cart(request)

    items = CartItem.objects.filter(cart=cart)

    serializer = CartItemSerializer(items, many=True)

    total_price = 0

    for item in items:
        total_price += item.quantity * item.product.price

    return Response({
        "cart_id": cart.id,
        "items": serializer.data,
        "total_price": total_price
    })

    


   

    # 🔥 MAIN LOGIC
  
        
@api_view(['POST'])
def update_cart_quantity_api(request):
    product_id=request.data.get("product_id")
    quantity=request.data.get('quantity')
    
    cart=get_or_create_cart(request)
    
    try:
        cart_item=CartItem.objects.get(cart=cart, product_id=product_id)
    
    except CartItem.DoesNotExist:
        return Response({'error': 'Item not found'},status=404)
    cart_item.quantity=quantity
    cart_item.save()
    
    return Response({'message':'quantity updated','quantity':cart_item.quantity})



@api_view(['POST'])
def clear_cart_api(request):
    cart=get_or_create_cart(request)
    CartItem.objects.filter(cart=cart).delete()
    return Response({'message':"Cart cleared"})



from django.db.models import Q

@api_view(['GET'])
def product_search_api(request):

    keyword = request.GET.get("keyword")

    products = Product.objects.filter(
        name__icontains=keyword
    )

    serializer = ProductSerializer(products, many=True)

    return Response(serializer.data)


@api_view(['GET'])
def product_filter_api(request):

    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    products = Product.objects.filter(
        price__gte=min_price,
        price__lte=max_price
    )

    serializer = ProductSerializer(products, many=True)

    return Response(serializer.data)

from django.core.paginator import Paginator

@api_view(['GET'])
def product_pagination_api(request):

    products = Product.objects.all()

    paginator = Paginator(products, 2)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    serializer = ProductSerializer(page_obj, many=True)

    return Response(serializer.data)


@api_view(['GET'])
def products_select_related_api(request):

    products = Product.objects.select_related('owner')

    serializer = ProductSerializer(products, many=True)

    return Response(serializer.data)

@api_view(['GET'])
def products_prefetch_related_api(request):
    products=Product.objects.prefetch_related('tags')
    serializer=ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def products_by_category_api(request, id):
    products=Product.objects.filter(category_id =id)
    serializer=ProductSerializer(products,many=True)
    return Response(serializer.data)

@api_view(['GET'])                                                   
def products_by_tag_api(request, id):
    products=Product.objects.filter(tags__id =id)
    serializer=ProductSerializer(products,many=True)
    return Response(serializer.data)



@api_view(['POST'])
def register_api(request):

    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User created successfully"})

    return Response(serializer.errors)


      