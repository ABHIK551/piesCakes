from django.shortcuts import render
from rest_framework import generics

# Create your views here.
def home(request):
    return render(request, 'static/index.html')

def profile(request):
    return render(request, 'static/pages-profile.html')

def login(request):
    return render(request, 'static/pages-sign-in.html')

def register(request):
    return render(request, 'static/pages-sign-up.html')

def categories(request):
    return render(request, 'static/categories.html')

def products(request):
    return render(request, 'static/product.html')

def banner(request):
    return render(request, 'static/banner.html')

def why_choose_us(request):
    return render(request, 'static/why-choose-us.html')

def top_picks(request):
    return render(request, 'static/top-picks.html')

def adds(request):
    return render(request, 'static/adds.html')

def baked_delights(request):
    return render(request,'static/baked-delight.html')


def customer_user(request):
    return render(request,'static/customer-users.html')

def orders(request):
    return render(request,'static/orders.html')
