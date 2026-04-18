from rest_framework import serializers
from .models import Product,CartItem

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__' 




class CartItemSerializer(serializers.ModelSerializer):
    
    product_name = serializers.CharField(source="product.name")
    price = serializers.FloatField(source="product.price")
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "product",
            "product_name",
            "price",
            "quantity",
            "subtotal"
        ]

    def get_subtotal(self, obj):
        return obj.quantity * obj.product.price
    
    
from django.contrib.auth.models import User

class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user