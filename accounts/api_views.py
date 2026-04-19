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

from .models import CartItem
from .serializers import CartItemSerializer
from .cart_utils import get_or_create_cart



@api_view(['POST'])
def register_api(request):

    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User created successfully"})

    return Response(serializer.errors)





@api_view(['POST'])
@permission_classes([AllowAny])  
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order_api(request):

    cart = get_or_create_cart(request)
    cart_items = CartItem.objects.filter(cart=cart)

    if not cart_items.exists():
        return Response({'error': 'Cart is empty'}, status=400)
    order = Order.objects.create(
        user=request.user
    )
    total_price = 0
    for item in cart_items:
        product = item.product
        if item.quantity > product.stock:
            return Response({
                "error": f"{product.name} out of stock"
            }, status=400)
            
        product.stock -= item.quantity
        product.save()
        
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item.quantity
        )
        total_price += product.price * item.quantity
 

    # cart empty
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

    # serializer use
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

    if product.stock <= 0:
        return Response({"error": "Product out of stock"}, status=400)

    if quantity > product.stock:
        return Response({"error": "Not enough stock"}, status=400)

    cart = get_or_create_cart(request)
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
     
    
    

 
