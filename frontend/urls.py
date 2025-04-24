from django.urls import path
from .views import refundPolicy, privacyPolicy, register,login, home, product, category, cart, orders

urlpatterns = [
    path('', home, name='home'),
    path('product/<str:product_id>', product, name='product'),
    path('login', login, name='login'),
    path('register', register, name='register'),
    path('category', category, name='category'),
    path('cart', cart, name='cart'),
    path('orders', orders, name='orders'),
    path('privacy-policy', privacyPolicy, name='privacyPolicy'),
    path('refund-policy', refundPolicy, name='refundPolicy'),
]