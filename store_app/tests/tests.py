import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from store_app.models import Category, Product, Order

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpass')

@pytest.fixture
def category():
    return Category.objects.create(name="Electronics", description="Electronic Items")

@pytest.fixture
def product(category):
    return Product.objects.create(
        name="Laptop",
        description="A high-performance laptop",
        price=1200.00,
        stock=10,
        category=category
    )

@pytest.fixture
def order(user, product):
    order = Order.objects.create(user=user, total_amount=1200.00)
    order.products.add(product)
    return order

@pytest.mark.django_db
def test_get_categories(api_client, category):
    response = api_client.get('/api/categories/')
    assert response.status_code == 200
    assert response.data[0]['name'] == category.name
    assert response.data[0]['description'] == category.description

@pytest.mark.django_db
def test_get_products(api_client, product):
    response = api_client.get('/api/products/')
    assert response.status_code == 200
    assert response.data[0]['name'] == product.name
    assert response.data[0]['description'] == product.description
    assert response.data[0]['price'] == str(product.price) 
    assert response.data[0]['stock'] == product.stock

@pytest.mark.django_db
def test_get_orders_authenticated(api_client, user, order):
    response = api_client.get('/api/orders/')
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['user'] == user.id
    assert response.data[0]['total_amount'] == str(order.total_amount)


@pytest.mark.django_db
def test_create_category(api_client):
    response = api_client.post('/api/categories/', {'name': 'Electronics', 'description': 'Devices and gadgets'})
    assert response.status_code == 201

@pytest.mark.django_db
def test_create_order_insufficient_stock(api_client, user): 
    category = Category.objects.create(name='Books')
    product = Product.objects.create(name='RAVNA', description='A beginner of Lanka', price=1050.0, stock=5, category=category)
    
    response = api_client.post('/api/orders/', {
        'user': user.id,
        'products': [{'product': product.id, 'quantity': 10}]
    })
    
    assert response.status_code == 400
    assert 'Insufficient stock' in str(response.data)
