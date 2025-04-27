from django.urls import path
from .views import orders, customer_user,home, baked_delights, profile, register, login, categories, products, banner, why_choose_us, top_picks, adds

urlpatterns = [
    path('', home, name='home'),
    path('profile', profile, name='profile'),
    path('login', login, name='login'),
    path('register', register, name='register'),
    path('categories', categories, name='categories'),
    path('products', products, name='products'),
    path('banner', banner, name='banner'),
    path('why-choose-us', why_choose_us, name='why-choose-us'),
    path('top-picks', top_picks, name='top-picks'),
    path('adds', adds, name='adds'),
    path('baked-delights', baked_delights, name='baked-delights'),
    path('customers', customer_user, name='customer_user'),
    path('orders', orders, name='orders'),
]