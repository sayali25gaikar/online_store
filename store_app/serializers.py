from .models import *
from rest_framework import serializers
from django.db import transaction


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'category']

class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True, write_only=True)

    def validate_products(self, products):
        for item in products:
            product = item['product']
            quantity = item['quantity']
            if product.stock < quantity:
                raise serializers.ValidationError(
                    f"Insufficient stock for {product.name}: Requested {quantity}, Available {product.stock}"
                )
        return products
    
    @transaction.atomic
    def create(self, validated_data):
        products_data = validated_data.pop('products')
        order = Order.objects.create(**validated_data)
        
        total_amount = 0
        order_products = []
        
        for item in products_data:
            product = item['product']
            quantity = item['quantity']
            product.stock -= quantity
            product.save()
            order_products.append(OrderProduct(order=order, product=product, quantity=quantity))
            total_amount += product.price * quantity
        
        OrderProduct.objects.bulk_create(order_products)
        order.total_amount = total_amount
        order.save()
        return order
