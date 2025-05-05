import base64
from django.shortcuts import render, get_object_or_404
from apis.models import Product
import os

def home(request):
    return render(request, 'frontend/index.html')

def product(request, product_id):
    try:
        # Decode base64 to get original product id (e.g., "1-piescakes")
        decoded_bytes = base64.b64decode(product_id)
        decoded_str = decoded_bytes.decode('utf-8')
        decoded_str_filtered = decoded_str.split("-")[0]
        print("decoded_str_filtered = " + decoded_str_filtered)
        # Assuming your `Product` model uses UUID or string-based IDs
        product = get_object_or_404(Product, id=decoded_str_filtered)

        
        context = {
            'product': product
        }

    except Exception as e:
        context = {
            'error': 'Invalid or missing product ID.',
        }

    return render(request, 'frontend/product.html', context)

def category(request):
    return render(request, 'frontend/categories.html')

def cart(request):
    return render(request, 'frontend/cart.html')

def orders(request):
    return render(request, 'frontend/orders.html')

def login(request):
    return render(request, 'frontend/login.html')

def register(request):
    return render(request, 'frontend/register.html')

def privacyPolicy(request):
    return render(request, 'frontend/privacy-policy.html')

def refundPolicy(request):
    return render(request, 'frontend/refund-policy.html')

def aboutUs(request):
    return render(request, 'frontend/about-us.html')

def termCon(request):
    return render(request, 'frontend/terms&Conditions.html')

from django.shortcuts import render, get_object_or_404
from django.http import Http404
from apis.models import CustomUser  # Assuming your user model is called User

def reset_password(request, uid, token):
    try:
        user = get_object_or_404(CustomUser, uid=uid)  # Fetch user based on uid
        # Validate the token here (you can use a custom method or Django's built-in token validation logic)
        if not user.validate_reset_token(token):  # Assuming you have a method to validate the token
            raise Http404("Invalid or expired token")
        
        # Render reset password page with uid and token
        return render(request, 'frontend/reset_password.html', {'uid': uid, 'token': token})
    except CustomUser.DoesNotExist:
        raise Http404("User not found")