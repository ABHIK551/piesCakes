from django.urls import path
from .views import gallery, contact, profile, reset_password, termCon, aboutUs, refundPolicy, privacyPolicy, register,login, home, product, category, cart, orders

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
    path('about-us', aboutUs, name='aboutUs'),
    path('profile', profile, name='profile'),
    path('contact-us', contact, name='contact'),
    path('gallery', gallery, name='gallery'),
    path('term-and-conditions', termCon, name='termCon'),
    path('reset-password/<uid>/<token>/', reset_password, name='reset_password'),
]