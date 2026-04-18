from django.contrib.auth.models import User
from django.db import models 
from django.utils import timezone




class Product(models.Model):
    name = models.CharField(max_length=100)
    description=models.TextField()
    price = models.IntegerField()  
    stock=models.IntegerField()
    created_at=models.DateTimeField(auto_now_add=True)
    text=models.TextField(max_length=500)
    
class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE, null=True,blank=True)
    session_key=models.CharField(max_length=40,null=True,blank=True)
    
        
class CartItem(models.Model):
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    STATUS_CHOICES=[('pending','Pending'),
                    ('processing','Processing'),
                    ('shipped','Shipped'),
                    ('delivered','Delivered'),
                    ('cancelled','Canclled'),]
    
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default='pending')
    def __str__(self):   # ✅ ভিতরে আনতে হবে
        return f'Order {self.id}' 

class OrderItem(models.Model):
    order=models.ForeignKey(Order,related_name='items',on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return self.product.name


