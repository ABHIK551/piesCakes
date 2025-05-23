from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.response import Response
from .models import Category,  Product
from .serializers import CategorySerializer, ProductSerializer
from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category
from .serializers import CategorySerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Category  # Assuming your model is named 'Category'
from .serializers import CategorySerializer
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Category
from .serializers import CategorySerializer
import base64
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from .models import Category
from .serializers import *
import base64
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .filters import ProductFilter
from rest_framework.views import APIView
import json
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser  # Adjust import if needed
from rest_framework import generics, permissions
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAdminUser 


class ProductCreateAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request, *args, **kwargs):

        # ✅ Flatten single-value lists from QueryDict
        data = {}
        for key, value in request.data.items():
            data[key] = value

        # ✅ Handle image files
        if 'product_images' in request.FILES:
            image_files = request.FILES.getlist('product_images')
            image_base64_list = []
            for image_file in image_files:
                try:
                    encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
                    image_base64_list.append(encoded_image)
                except Exception as e:
                    return Response({"success": False, "message": f"Image error: {str(e)}"}, status=400)
            data['product_images_base64'] = ",".join(image_base64_list)

        # ✅ Parse serving_sizes_input from JSON string
        serving_sizes_input_raw = request.data.get("serving_sizes_input")
        if serving_sizes_input_raw:
            try:
                parsed_serving_sizes = json.loads(serving_sizes_input_raw)
                data['serving_sizes_input'] = parsed_serving_sizes
            except json.JSONDecodeError:
                return Response({"success": False, "message": "Invalid JSON for serving_sizes_input"}, status=400)

        # ✅ Serialize and create product
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            product = serializer.save()
            return Response({
                "success": True,
                "message": "Product created successfully!",
                "data": ProductSerializer(product).data
            }, status=201)

        return Response({"success": False, "errors": serializer.errors}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def create(self, request, *args, **kwargs):
        # Extract request data
        data = request.data.dict() if isinstance(request.data, dict) else request.data.copy()

        # Handle file upload (multipart/form-data)
        image_file = request.FILES.get('image_file')
        if image_file:
            try:
                image_binary = image_file.read()
                base64_encoded_image = base64.b64encode(image_binary).decode("utf-8")
                data["image_base64"] = base64_encoded_image  # ✅ Save as base64 string
            except Exception as e:
                return Response({"success": False, "errors": {"image_file": [str(e)]}}, status=status.HTTP_400_BAD_REQUEST)

        # Convert data to a dictionary (if it's still a QueryDict)
        category_data = {
            "name": data.get("name"),
            "description": data.get("description"),
            "status": data.get("status"),
            "parent": data.get("parent"),
            "image_base64": data.get("image_base64", None),
        }

        # Validate and save data
        serializer = self.get_serializer(data=category_data)
        if serializer.is_valid():
            category = serializer.save()
            return Response({
                "success": True,
                "message": "Category created successfully!",
                "category": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)     

class CustomPagination(PageNumberPagination):
    page_size = 10 # Default page size
    page_size_query_param = 'pageSize'  # Allow clients to define page size
    max_page_size = 100  # Limit max page size

    def get_paginated_response(self, data):
        return Response({
            "success": True,
            "page": self.page.number,
            "pageSize": self.page_size,
            "totalRecords": self.page.paginator.count,
            "totalPages": self.page.paginator.num_pages,
            "categories": data
        })
    
class CustomPaginationProduct(PageNumberPagination):
    page_size = 5 # Default page size
    page_size_query_param = 'pageSize'  # Allow clients to define page size
    max_page_size = 100  # Limit max page size

    def get_paginated_response(self, data):
        return Response({
            "success": True,
            "page": self.page.number,
            "pageSize": self.page_size,
            "totalRecords": self.page.paginator.count,
            "totalPages": self.page.paginator.num_pages,
            "products": data
        })

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = CustomPaginationProduct
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'category', 'price']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'price']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            data = self.format_product_data(page)
            return self.get_paginated_response(data)

        data = self.format_product_data(queryset)
        return Response({"success": True, "products": data}, status=status.HTTP_200_OK)

    def format_product_data(self, queryset):
        products = []

        for product in queryset:
            # Get related serving sizes for this product
            serving_sizes_qs = product.serving_sizes.all()
            serving_sizes = ProductServingSizeSerializer(serving_sizes_qs, many=True).data

            product_data = {
                "id": product.id,
                "name": product.name,
                "category": {
                    "id": product.category.id,
                    "name": product.category.name,
                    "parent": {
                        "id": product.category.parent.id,
                        "name": product.category.parent.name
                    } if product.category.parent else None
                } if product.category else None,
                "description": product.description,
                "ingredients": product.ingredients,
                "allergen_info": product.allergen_info,
                "price": product.price,
                "discount_price": product.discount_price,
                "stock_status": product.stock_status,
                "serving_size": product.serving_size,
                "serving_sizes": serving_sizes,  # ✅ Fixed line
                "total_stock": product.total_stock,
                "reorder_level": product.reorder_level,
                "weight": product.weight,
                "cake_size": product.cake_size,
                "flavor_variants": product.flavor_variants,
                "add_ons": product.add_ons,
                "product_images": product.product_images_base64.split(',') if product.product_images_base64 else [],
                "calories": product.calories,
                "nutrition_facts": product.nutrition_facts,
                "prep_time": product.prep_time,
                "delivery_option": product.delivery_option,
                "shelf_life": product.shelf_life,
                "tags": product.tags,
                "reviews": product.reviews,
                "related_products": product.related_products,
                "total_sales": product.total_sales,
                "status": 'Active' if product.status == 1 else 'Inactive',
                "created_at": product.created_at,
                "updated_at": product.updated_at
            }

            products.append(product_data)

        return {"products": products}


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()  # Fetch all categories
    serializer_class = CategorySerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'parent']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'updated_at']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            data = self.format_category_data(page)
            return self.get_paginated_response(data)

        # If pagination is disabled, return full dataset
        data = self.format_category_data(queryset)
        return Response({"success": True, "categories": data}, status=status.HTTP_200_OK)

    def format_category_data(self, queryset):
        """ Format categories in a single list, including parent info if it's a subcategory """
        categories = []

        for category in queryset:
            category_data = {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "status": category.status,
                "image": category.image_base64,
                "created_at": category.created_at,
                "updated_at": category.updated_at,
                "parent": {
                    "id": category.parent.id,
                    "name": category.parent.name
                } if category.parent else None  # Include parent info if it's a subcategory
            }
            categories.append(category_data)

        return {"main_categories": categories}
    
@api_view(['GET'])
def main_categories(request):
    """Fetch only main categories (categories without a parent)"""
    main_categories = Category.objects.filter(parent__isnull=True)  # Fetch only main categories
    serializer = CategorySerializer(main_categories, many=True)
    return Response(serializer.data)

@api_view(["PUT", "PATCH"])
@parser_classes([MultiPartParser, FormParser])
def update_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    data = request.data.copy()

    # Handle image upload (Convert to Base64)
    if "image" in request.FILES:
        image_file = request.FILES["image"]
        data["image_base64"] = base64.b64encode(image_file.read()).decode("utf-8")

    serializer = CategorySerializer(category, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "success": True,
            "message": "Category updated successfully!",
            "category": serializer.data
        }, status=status.HTTP_200_OK)

    return Response({
        "success": False,
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(["DELETE"])
def delete_category(request, category_id):
    # Check if category exists
    category = Category.objects.filter(id=category_id).first()
    
    if not category:
        return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

    # Check if this category is referenced as a parent by any other category
    if Category.objects.filter(parent_id=category_id).exists():
        return Response(
            {"error": "Cannot delete this category because it has dependent subcategories."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    category.delete()
    
    # ✅ Change status code to 200 so it includes a response body
    return Response({"message": "Category deleted successfully!", "success": True}, status=status.HTTP_200_OK)


@api_view(["DELETE"])
def delete_product(request, product_id):
    # Check if category exists
    product = Product.objects.filter(id=product_id).first()
    
    if not product:
        return Response({"error": "Product not found."}, status=status.HTTP_208_ALREADY_REPORTED)

    product.delete()
    
    # ✅ Change status code to 200 so it includes a response body
    return Response({"message": "Product deleted successfully!", "success": True}, status=status.HTTP_200_OK)


# @api_view(["PUT", "PATCH", "POST"])
# @parser_classes([MultiPartParser, FormParser])
# def update_product(request, productId):
#     product = get_object_or_404(Product, id=productId)
#     data = request.data.copy()

#     # Handle image upload (Convert to Base64)
#     if "image" in request.FILES:
#         image_file = request.FILES["image"]
#         data["image_base64"] = base64.b64encode(image_file.read()).decode("utf-8")

#     # Convert "Active" / "Inactive" to boolean
#     if "status" in data:
#         data["status"] = data["status"] == "Active"

#     serializer = ProductSerializer(product, data=data, partial=True)
#     if serializer.is_valid():
#         serializer.save()
#         return Response({
#             "success": True,
#             "message": "Product updated successfully!",
#             "product": serializer.data
#         }, status=status.HTTP_200_OK)

#     return Response({
#         "success": False,
#         "errors": serializer.errors
#     }, status=status.HTTP_400_BAD_REQUEST)


# @api_view(["PUT", "PATCH", "POST"])
# @parser_classes([MultiPartParser, FormParser, JSONParser])
# def update_product(request, productId):
#     product = get_object_or_404(Product, id=productId)
#     data = request.data.copy()
    
#     print(f"Date come to update for the product is {data}")

#     # ✅ Convert "Active" / "Inactive" to boolean
#     if "status" in data:
#         data["status"] = data["status"] == "Active"

#     # ✅ Handle image upload (Convert to Base64)
#     if "image" in request.FILES:
#         image_file = request.FILES["image"]
#         try:
#             data["image_base64"] = base64.b64encode(image_file.read()).decode("utf-8")
#         except Exception as e:
#             return Response({"success": False, "message": f"Image error: {str(e)}"}, status=400)

#     # ✅ Handle product_images (multiple images)
#     if 'product_images' in request.FILES:
#         image_files = request.FILES.getlist('product_images')
#         image_base64_list = []
#         for image_file in image_files:
#             try:
#                 encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
#                 image_base64_list.append(encoded_image)
#             except Exception as e:
#                 return Response({"success": False, "message": f"Image error: {str(e)}"}, status=400)
#         data['product_images_base64'] = ",".join(image_base64_list)

#     # ✅ Parse serving_sizes_input from JSON string
#     serving_sizes_input_raw = request.data.get("serving_sizes_input")
#     if serving_sizes_input_raw:
#         try:
#             parsed_serving_sizes = json.loads(serving_sizes_input_raw)
#             data['serving_sizes_input'] = parsed_serving_sizes
#         except json.JSONDecodeError:
#             return Response({"success": False, "message": "Invalid JSON for serving_sizes_input"}, status=400)

#     # ✅ Serialize and update product
#     serializer = ProductSerializer(product, data=data, partial=True)
#     if serializer.is_valid():
#         updated_product = serializer.save()
#         return Response({
#             "success": True,
#             "message": "Product updated successfully!",
#             "product": ProductSerializer(updated_product).data
#         }, status=status.HTTP_200_OK)

#     return Response({
#         "success": False,
#         "errors": serializer.errors
#     }, status=status.HTTP_400_BAD_REQUEST)

@api_view(["PUT", "PATCH", "POST"])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def update_product(request, productId):
    product = get_object_or_404(Product, id=productId)

    # ✅ Flatten and collect all data
    data = {}
    for key, value in request.data.items():
        data[key] = value


    # ✅ Handle image upload (Base64 encode single or multiple images)
    if "product_images" in request.FILES:
        image_files = request.FILES.getlist("product_images")
        image_base64_list = []
        for image in image_files:
            try:
                encoded = base64.b64encode(image.read()).decode("utf-8")
                image_base64_list.append(encoded)
            except Exception as e:
                return Response({"success": False, "message": f"Image error: {str(e)}"}, status=400)
        data["product_images_base64"] = ",".join(image_base64_list)

    elif "image" in request.FILES:
        # Fallback: single image case
        image = request.FILES["image"]
        try:
            encoded = base64.b64encode(image.read()).decode("utf-8")
            data["image_base64"] = encoded
        except Exception as e:
            return Response({"success": False, "message": f"Image error: {str(e)}"}, status=400)

    # ✅ Convert "Active"/"Inactive" to boolean
    if "status" in data:
        data["status"] = data["status"] == "Active"

    # ✅ Parse serving_sizes_input JSON
    serving_sizes_input_raw = request.data.get("serving_sizes_input")
    if serving_sizes_input_raw:
        try:
            parsed_serving_sizes = json.loads(serving_sizes_input_raw)
            data["serving_sizes_input"] = parsed_serving_sizes
        except json.JSONDecodeError:
            return Response({"success": False, "message": "Invalid JSON for serving_sizes_input"}, status=400)

    # ✅ Partial update
    serializer = ProductSerializer(product, data=data, partial=True)
    if serializer.is_valid():
        product = serializer.save()
        return Response({
            "success": True,
            "message": "Product updated successfully!",
            "product": serializer.data
        }, status=status.HTTP_200_OK)

    return Response({
        "success": False,
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            
            # Prepare welcome email
            html_body = f"""
                <h2>Welcome to Pies & Thies!</h2>
                <p>Hi {serializer.validated_data.get('first_name', 'there')},</p>
                <p>Thank you for registering with <strong>Pies & Thies</strong>. We're thrilled to have you on board.</p>
                <p>Start exploring our delicious selections, and if you ever need help, our team is just a message away.</p>
                <br/>
                <p>Happy shopping!<br/><strong>Pies & Thies Team</strong></p>
            """
            try:
                send_email(
                    subject="🎉 Welcome to Pies & Thies – Let’s Get Started!",
                    html_message=html_body,
                    to_email=serializer.validated_data["email"]
                )
            except Exception as e:
                print("Email failed:", str(e))  # Optionally log this

            return Response({"message": "Registration successful.", "status": "success"}, status=status.HTTP_201_CREATED)

        error = serializer.errors.get("message") or next(iter(serializer.errors.values()))[0]
        return Response({"message": error, "status": "error"}, status=status.HTTP_400_BAD_REQUEST)

import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta

# class LoginView(APIView):
#     def post(self, request):
#         email = request.data.get("email")
#         password = request.data.get("password")

#         if not email or not password:
#             return Response({"success": False, "message": "Email and password required."}, status=status.HTTP_400_BAD_REQUEST)

#         user = authenticate(request, username=email, password=password)

#         if user is not None:
#             # ✅ Generate JWT token
#             payload = {
#                 "user_id": user.id,
#                 "email": user.email,
#                 "exp": datetime.utcnow() + timedelta(hours=2),  # Token expires in 2 hours
#                 "iat": datetime.utcnow()
#             }
#             token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

#             return Response({
#                 "success": True,
#                 "message": "Login successful",
#                 "token": token,
#                 "user": {
#                     "id": user.id,
#                     "email": user.email,
#                     "name": f"{user.first_name} {user.last_name}"
#                 }
#             })
#         else:
#             return Response({"success": False, "message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# class LoginView(APIView):
#     def post(self, request):
#         email = request.data.get("email")
#         password = request.data.get("password")

#         if not email or not password:
#             return Response({"success": False, "message": "Email and password required."}, status=status.HTTP_400_BAD_REQUEST)

#         user = authenticate(request, username=email, password=password)

#         if user is not None:
#             # ✅ Generate JWT token
#             payload = {
#                 "user_id": user.id,
#                 "email": user.email,
#                 "exp": datetime.utcnow() + timedelta(hours=2),
#                 "iat": datetime.utcnow()
#             }
#             token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

#             # ✅ Prepare email HTML body
#             html_body = f"""
#                 <div style="font-family: Arial, sans-serif; padding: 20px; background-color: #f9f5f2; color: #333;">
#                     <h2 style="color: #b05a3c;">Welcome back to Pies & Thies!</h2>
#                     <p>Hi {user.first_name},</p>
#                     <p>
#                         We noticed a successful login to your account just now:
#                     </p>
#                     <ul>
#                         <li><strong>Email:</strong> {user.email}</li>
#                         <li><strong>Time (UTC):</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}</li>
#                     </ul>
#                     <p>
#                         If this was you, no action is needed. If you didn’t authorize this login,
#                         please <a href="mailto:support@piesandthies.com" style="color: #b05a3c;">contact our support team</a> immediately.
#                     </p>
#                     <hr style="margin: 20px 0;" />
#                     <p style="font-size: 14px; color: #666;">
#                         Thanks for choosing <strong>Pies & Thies</strong> – where every bite feels like home.
#                     </p>
#                 </div>
#             """


#             # ✅ Send email
#             try:
#                 send_email("🔐 New Login to Your Pies & Thies Account – Was this you?n", html_body, user.email)
#             except Exception as e:
#                 # Log this if needed, or ignore silently
#                 print("Email failed:", str(e))

#             return Response({
#                 "success": True,
#                 "message": "Login successful",
#                 "token": token,
#                 "user": {
#                     "id": user.id,
#                     "email": user.email,
#                     "name": f"{user.first_name} {user.last_name}"
#                 }
#             })

#         else:
#             return Response({"success": False, "message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class LoginView(APIView):
    """
    POST /api/auth/login/
    {
      "email": "user@example.com",
      "password": "secret"
    }
    → returns access+refresh tokens and user info
    """
    permission_classes = []    # allow any

    def post(self, request):
        email = request.data.get("email", "").strip()
        password = request.data.get("password", "")

        if not email or not password:
            return Response(
                {"success": False, "message": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=email, password=password)
        if not user:
            return Response(
                {"success": False, "message": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if not user.is_active:
            return Response(
                {"success": False, "message": "Account is disabled."},
                status=status.HTTP_403_FORBIDDEN
            )

        # ─── Generate tokens ───────────────────────────────────────────────────
        refresh = RefreshToken.for_user(user)
        access  = refresh.access_token

        # Optional: customize access token lifetime (default is from settings)
        # access.set_exp(from_time=timezone.now(), lifetime=timedelta(hours=2))

        # ─── Send login notification email ────────────────────────────────────
        html_body = f"""
        <div style="font-family: Arial, sans-serif; background:#f9f5f2; padding:20px;">
          <h2 style="color:#b05a3c;">Welcome back to Pies & Thies!</h2>
          <p>Hi {user.first_name},</p>
          <p>Your account was just accessed:</p>
          <ul>
            <li><strong>Email:</strong> {user.email}</li>
            <li><strong>Time (UTC):</strong> {datetime.utcnow():%Y-%m-%d %H:%M:%S}</li>
          </ul>
          <p>If this wasn’t you, <a href="mailto:support@piesandthies.com" style="color:#b05a3c;">please contact support</a> immediately.</p>
          <hr/>
          <p style="color:#666; font-size:14px;">
            Thanks for choosing <strong>Pies & Thies</strong>.
          </p>
        </div>
        """
        try:
            send_email(
                subject="🔐 New Login to Your Pies & Thies Account",
                html_body=html_body,
                to_email=user.email
            )
        except Exception as e:
            # log error if you like
            print("Failed to send login email:", e)

        # ─── Build response ────────────────────────────────────────────────────
        return Response({
            "success": True,
            "message": "Login successful.",
            "token_type": "Bearer",
            "access_token":  str(access),
            "refresh_token": str(refresh),
            "expires_in":    access.lifetime.total_seconds(),
            "user": {
                "id":        user.id,
                "email":     user.email,
                "first_name":user.first_name,
                "last_name": user.last_name,
            }
        }, status=status.HTTP_200_OK)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Banner
from .serializers import BannerSerializer


import base64
import uuid
import imghdr
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import BannerSerializer


class BannerCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data.copy()

        # If image is uploaded as a file, convert to base64
        if "image" in request.FILES:
            image_file = request.FILES["image"]
            base64_str = base64.b64encode(image_file.read()).decode("utf-8")
            data["image"] = base64_str

        serializer = BannerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomPaginationMain(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'pageSize'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            "success": True,
            "page": self.page.number,
            "pageSize": self.page.paginator.per_page,
            "totalRecords": self.page.paginator.count,
            "totalPages": self.page.paginator.num_pages,
            "data": data
        })
    
from rest_framework.generics import ListAPIView

class BannerListView(ListAPIView):
    queryset = Banner.objects.all().order_by('-created_at')
    serializer_class = BannerSerializer
    pagination_class = CustomPaginationMain

class BannerDeleteAPIView(APIView):
    def post(self, request, pk, *args, **kwargs):
        banner = get_object_or_404(Banner, pk=pk)
        banner.delete()
        return Response({"success": True, "message": "Banner deleted successfully."}, status=status.HTTP_200_OK)
    
@api_view(['GET'])
def get_banner_by_id(request, banner_id):
    try:
        banner = Banner.objects.get(id=banner_id)
        serializer = BannerSerializer(banner)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    except Banner.DoesNotExist:
        return Response({"success": False, "message": "Banner not found"}, status=status.HTTP_404_NOT_FOUND)
    
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Banner
import json

@api_view(['POST'])
def update_banner(request, pk):
    # Get the banner object or return 404 if not found
    banner = get_object_or_404(Banner, pk=pk)
    
    # Prepare the data to update
    data = request.data.copy()  # Make a copy of request data to modify
    
    # If image is uploaded as a file, convert to base64 and update the 'image' field
    if "image_base64" in request.FILES:
        image_file = request.FILES["image_base64"]
        base64_str = base64.b64encode(image_file.read()).decode("utf-8")
        data["image"] = base64_str
    
    # If image is provided as a base64 string in the request
    elif "image" in request.data:
        base64_str = request.data["image"]
        # You can add extra validation here to ensure it's valid base64

        # Optionally, you could decode base64 and save as a file or keep as base64
        data["image"] = base64_str

    # Use the serializer to validate and update the banner
    serializer = BannerSerializer(banner, data=data)
    
    # Create or update the serializer with the banner instance and new data
    serializer = BannerSerializer(banner, data=data)

    # Validate and save the serializer
    if serializer.is_valid():
        serializer.save()  # Save the updated banner

        # Return a success response
        return Response({
            "success": True,
            "message": "Banner updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    # If validation fails, return the errors with a message
    return Response({
        "success": False,
        "message": "Failed to update banner",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

from .models import WhyChooseUs
from .serializers import WhyChooseUsSerializer


class WhyChooseUsCreateAPIView(generics.CreateAPIView):
    queryset = WhyChooseUs.objects.all()
    serializer_class = WhyChooseUsSerializer
    parser_classes = [MultiPartParser, FormParser]  # Allow file uploads

    def post(self, request, *args, **kwargs):
        # Get image file from request.FILES
        image_file = request.FILES.get('image')
        
        if image_file:
            # Read and encode image to base64
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            mime_type = image_file.content_type
            base64_string = f'data:{mime_type};base64,{base64_image}'

            # Make a mutable copy of request.data and replace 'image'
            data = request.data.copy()
            data['image'] = base64_string
        else:
            return Response({'error': 'Image file is required.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
import base64
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import WhyChooseUs
from .serializers import WhyChooseUsSerializer
from django.http import Http404

    
class WhyChooseUsListAPIView(generics.ListAPIView):
    queryset = WhyChooseUs.objects.all().order_by('order')  # Optional: Ordering by display order
    serializer_class = WhyChooseUsSerializer
    pagination_class = CustomPaginationMain  # Set custom pagination class

class WhyChooseUsDeleteAPIView(generics.DestroyAPIView):
    queryset = WhyChooseUs.objects.all()
    serializer_class = WhyChooseUsSerializer

    def get_object(self):
        # Get the Base64 encoded ID from the URL
        encoded_id = self.kwargs['pk']
        # Decode the Base64 ID to the original UUID
        try:
            decoded_id = base64.b64decode(encoded_id).decode('utf-8')
            # Convert to UUID object
            uuid_object = uuid.UUID(decoded_id)
        except (ValueError, TypeError):
            raise Http404("Invalid UUID format")

        # Retrieve the object with the decoded UUID
        try:
            return WhyChooseUs.objects.get(id=uuid_object)
        except WhyChooseUs.DoesNotExist:
            raise Http404("Item not found")

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()  # Delete the object
        return Response(
            {"success": True, "message": "Item deleted successfully"},
            status=status.HTTP_200_OK
        )
    

@api_view(['POST'])
def update_why_choose_us(request):
    item_id = request.data.get('id')

    if not item_id:
        return Response({"error": "ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        item = WhyChooseUs.objects.get(id=item_id)
    except WhyChooseUs.DoesNotExist:
        return Response({"error": "Item not found."}, status=status.HTTP_404_NOT_FOUND)
    data = request.data.copy()
    image_file = request.FILES.get('image')
    if image_file and image_file.name.strip() != "":
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        mime_type = image_file.content_type
        base64_string = f'data:{mime_type};base64,{base64_image}'
        data['image'] = base64_string
    else:
        data.pop('image', None)
    serializer = WhyChooseUsSerializer(item, data=data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Item updated successfully.",
            "image": item.image
        }, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TopPickBackgroundCreateView(APIView):
    def post(self, request, *args, **kwargs):
        # Make request data mutable
        data = request.data.copy()
        
        image_file = request.FILES.get('image', None)
        
        if image_file:
            # Convert file to base64 string
            buffer = BytesIO()
            buffer.write(image_file.read())
            base64_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
            content_type = image_file.content_type or 'image/jpeg'
            base64_image = f"data:{content_type};base64,{base64_str}"
            data['image'] = base64_image
        
        serializer = TopPickBackgroundSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
from rest_framework.generics import ListCreateAPIView

# 3. View to List All Data with Pagination
class TopPickBackgroundListView(ListAPIView):
    queryset = TopPickBackground.objects.all()
    serializer_class = TopPickBackgroundSerializer
    pagination_class = CustomPaginationMain  # Using custom pagination

class TopPickBackgroundDeleteView(APIView):
    def post(self, request, encoded_id, *args, **kwargs):
        try:
            decoded_id = int(base64.b64decode(encoded_id).decode("utf-8"))
            obj = TopPickBackground.objects.get(id=decoded_id)
            obj.delete()
            return Response({"success": True, "message": "Deleted successfully."}, status=status.HTTP_200_OK)
        except TopPickBackground.DoesNotExist:
            return Response({"success": False, "message": "Item not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"success": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
@csrf_exempt  # Optional if you are not using CSRF tokens
def update_top_pick(request):
    if request.method == 'POST':
        try:
            # Getting the ID and other form fields from the POST data
            top_pick_id = request.POST.get('top_pick_id')
            heading = request.POST.get('heading')
            description = request.POST.get('description')
            status = request.POST.get('status')
            link = request.POST.get('link')
            image_base64 = request.POST.get('image_base64')  # The image as base64
            new_image_file = request.FILES.get('image')  # The image file (if provided)
            
            # Fetch the existing TopPick object
            top_pick = TopPickBackground.objects.get(id=top_pick_id)

            # If a new image file is provided, convert it to base64 and save it
            if new_image_file:
                # Convert the file to base64 and save it
                image = ContentFile(new_image_file.read(), name=new_image_file.name)
                top_pick.image.save(new_image_file.name, image, save=True)

            elif image_base64:
                # If a base64 image is provided, convert it and save it
                format, imgstr = image_base64.split(';base64,') 
                imgdata = base64.b64decode(imgstr)
                image = ContentFile(imgdata, name="image.jpg")
                top_pick.image.save("top_pick_image.jpg", image, save=True)

            # Update other fields
            top_pick.heading = heading
            top_pick.description = description
            top_pick.status = status
            top_pick.link = link

            # Save the object
            top_pick.save()

            return JsonResponse({'message': 'Top Pick updated successfully', 'status': 'success', 'id': top_pick.id})
        except Exception as e:
            return JsonResponse({'message': str(e), 'status': 'error'})
    else:
        return JsonResponse({'message': 'Invalid request method', 'status': 'error'})
    


class AddCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data.copy()

        # If image is uploaded as a file, convert to base64
        if "image" in request.FILES:
            image_file = request.FILES["image"]
            base64_str = base64.b64encode(image_file.read()).decode("utf-8")
            data["image"] = base64_str

        serializer = AdsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AdsListView(ListAPIView):
    queryset = Adds.objects.all().order_by('-created_at')
    serializer_class = AdsSerializer
    pagination_class = CustomPaginationMain

class AddsDeleteAPIView(APIView):
    def post(self, request, pk, *args, **kwargs):
        ads = get_object_or_404(Adds, pk=pk)
        ads.delete()
        return Response({"success": True, "message": "Ad deleted successfully."}, status=status.HTTP_200_OK)
    
@api_view(['GET'])
def get_ads_by_id(request, id):
    try:
        ads = Adds.objects.get(id=id)
        serializer = AdsSerializer(ads)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    except Adds.DoesNotExist:
        return Response({"success": False, "message": "Add not found"}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
def ads_banner(request, pk):
    # Get the banner object or return 404 if not found
    ads = get_object_or_404(Adds, pk=pk)
    
    # Prepare the data to update
    data = request.data.copy()  # Make a copy of request data to modify
    
    # If image is uploaded as a file, convert to base64 and update the 'image' field
    if "image_base64" in request.FILES:
        image_file = request.FILES["image_base64"]
        base64_str = base64.b64encode(image_file.read()).decode("utf-8")
        data["image"] = base64_str
    
    # If image is provided as a base64 string in the request
    elif "image" in request.data:
        base64_str = request.data["image"]
        # You can add extra validation here to ensure it's valid base64

        # Optionally, you could decode base64 and save as a file or keep as base64
        data["image"] = base64_str

    # Use the serializer to validate and update the banner
    serializer = AdsSerializer(ads, data=data)
    
    # Create or update the serializer with the banner instance and new data
    serializer = AdsSerializer(ads, data=data)

    # Validate and save the serializer
    if serializer.is_valid():
        serializer.save()  # Save the updated banner

        # Return a success response
        return Response({
            "success": True,
            "message": "Banner updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    # If validation fails, return the errors with a message
    return Response({
        "success": False,
        "message": "Failed to update banner",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


class BakedDelightsCreateAPIView(generics.CreateAPIView):
    queryset = BakedDelight.objects.all()
    serializer_class = BakedDelightsSerializer
    parser_classes = [MultiPartParser, FormParser]  # Allow file uploads

    def post(self, request, *args, **kwargs):
        image_file = request.FILES.get('image')
        
        data = request.data.copy()  # Make it mutable

        status_str = data.get('status', '').lower()
        if status_str == '1':
            data['status'] = True
        elif status_str == '0':
            data['status'] = False
        else:
            data['status'] = False  # Default/fallback (or you could return an error)

        if image_file:
            # Encode image to base64
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            mime_type = image_file.content_type
            base64_string = f'data:{mime_type};base64,{base64_image}'

            # Replace 'image' in data
            data = request.data.copy()
            data['image'] = base64_string
        else:
            return Response({'error': 'Image file is required.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Print and return serializer validation errors
            print("Serializer errors:", serializer.errors)
            return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
class BakedDelightListAPIView(generics.ListAPIView):
    queryset = BakedDelight.objects.all().order_by('order')  # Optional: Ordering by display order
    serializer_class = BakedDelightsSerializer
    pagination_class = CustomPaginationMain  # Set custom pagination class

class BakedDelightDeleteAPIView(generics.DestroyAPIView):
    queryset = BakedDelight.objects.all()
    serializer_class = BakedDelightsSerializer

    def get_object(self):
        # Get the Base64 encoded ID from the URL
        encoded_id = self.kwargs['pk']
        # Decode the Base64 ID to the original UUID
        try:
            decoded_id = base64.b64decode(encoded_id).decode('utf-8')
            # Convert to UUID object
            uuid_object = uuid.UUID(decoded_id)
        except (ValueError, TypeError):
            raise Http404("Invalid UUID format")

        # Retrieve the object with the decoded UUID
        try:
            return BakedDelight.objects.get(id=uuid_object)
        except BakedDelight.DoesNotExist:
            raise Http404("Item not found")

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()  # Delete the object
        return Response(
            {"success": True, "message": "Item deleted successfully"},
            status=status.HTTP_200_OK
        )
    


@api_view(['POST'])
def update_baked_delights(request):
    item_id = request.data.get('id')

    if not item_id:
        return Response({"error": "ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        item = BakedDelight.objects.get(id=item_id)
    except BakedDelight.DoesNotExist:
        return Response({"error": "Item not found."}, status=status.HTTP_404_NOT_FOUND)
    data = request.data.copy()
    image_file = request.FILES.get('image')
    if image_file and image_file.name.strip() != "":
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        mime_type = image_file.content_type
        base64_string = f'data:{mime_type};base64,{base64_image}'
        data['image'] = base64_string
    else:
        data.pop('image', None)
    serializer = BakedDelightsSerializer(item, data=data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Item updated successfully.",
            "image": item.image
        }, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# @api_view(['POST'])
# def add_to_cart(request):
#     if request.method == 'POST':
#         # Extract userId and productIds from the request data
#         user_id = request.data.get('userId')
#         product_ids = request.data.get('productIds')

#         # If productIds is not a list, convert it into one
#         if isinstance(product_ids, int):  # If it's a single integer
#             product_ids = [product_ids]
#         elif not isinstance(product_ids, list):  # If it's neither a list nor a single integer
#             return Response({'error': 'productIds should be a list or a single integer.'}, status=status.HTTP_400_BAD_REQUEST)

#         if not user_id or not product_ids:
#             return Response({'error': 'userId and productIds are required.'}, status=status.HTTP_400_BAD_REQUEST)

#         # Get the user object
#         try:
#             user = CustomUser.objects.get(id=user_id)
#         except CustomUser.DoesNotExist:
#             return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

#         # Get the products
#         products = Product.objects.filter(id__in=product_ids)

#         # If no products were found with the given IDs
#         if not products.exists():
#             return Response({'error': 'Some products not found.'}, status=status.HTTP_404_NOT_FOUND)

#         # Get or create the user's cart
#         cart, created = Cart.objects.get_or_create(user=user)

#         # Add products to the cart
#         cart.products.add(*products)
#         cart.save()

#         # Serialize the cart and return the response
#         from .serializers import CartSerializer
#         serializer = CartSerializer(cart)
#         return Response(serializer.data, status=status.HTTP_200_OK)


# @api_view(['POST'])
# def add_to_cart(request):
#     if request.method == 'POST':
#         user_id = request.data.get('userId')
#         cart_items_data = request.data.get('cartItems', [])

#         if not user_id or not cart_items_data:
#             return Response({'error': 'userId and cartItems are required.'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             user = CustomUser.objects.get(id=user_id)
#         except CustomUser.DoesNotExist:
#             return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

#         # Get or create cart
#         cart, created = Cart.objects.get_or_create(user=user)

#         # Optionally clear existing items (depends on whether you're replacing or appending)
#         cart.cart_items.all().delete()

#         for item in cart_items_data:
#             product_id = item.get('product')
#             quantity = item.get('quantity', 1)  # Default quantity = 1

#             try:
#                 product = Product.objects.get(id=product_id)
#                 CartItem.objects.create(cart=cart, product=product, quantity=quantity)
#             except Product.DoesNotExist:
#                 continue  # Or handle error if needed

#         # Serialize and return updated cart
#         serializer = CartSerializer(cart)
#         return Response(serializer.data, status=status.HTTP_200_OK)

# @api_view(['POST'])
# def add_to_cart(request):
#     user_id = request.data.get('userId')
#     cart_items_data = request.data.get('cartItems', [])

#     if not user_id or not cart_items_data:
#         return Response({'error': 'userId and cartItems are required.'}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         user = CustomUser.objects.get(id=user_id)
#     except CustomUser.DoesNotExist:
#         return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

#     # Get or create cart
#     cart, created = Cart.objects.get_or_create(user=user)

#     for item in cart_items_data:
#         product_id = item.get('product')
#         quantity = item.get('quantity', 1)

#         try:
#             product = Product.objects.get(id=product_id)
#         except Product.DoesNotExist:
#             continue  # Skip if product doesn't exist

#         # Check if this product is already in the cart
#         cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

#         if item_created:
#             cart_item.quantity = quantity  # Set quantity if new item
#         else:
#             cart_item.quantity += quantity  # Increase quantity if item exists

#         cart_item.save()

#     serializer = CartSerializer(cart)
#     return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def add_to_cart(request):
    user_id = request.data.get('userId')
    cart_items_data = request.data.get('cartItems', [])

    if not user_id or not cart_items_data:
        return Response({'error': 'userId and cartItems are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Get or create cart
    cart, created = Cart.objects.get_or_create(user=user)

    for item in cart_items_data:
        product_id = item.get('product')
        quantity = item.get('quantity', 1)
        size = item.get('size', 'default')
        price = item.get('price', 0.0)
        discount_price = item.get('discount_price', 0.0)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue  # Skip if product doesn't exist

        # Check if this product with the same size exists in cart
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            size=size  # Include size in uniqueness logic
        )

        if item_created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity

        cart_item.price = price
        cart_item.discount_price = discount_price
        cart_item.save()

    serializer = CartSerializer(cart)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['GET'])
def view_cart(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        cart, created = Cart.objects.get_or_create(user=user)

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

# @api_view(['DELETE'])
# def delete_cart_item(request, user_id, product_id):
#     try:
#         user = CustomUser.objects.get(id=user_id)
#         cart = Cart.objects.get(user=user)
#         cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        
#         cart_item.delete()

#         return Response({'message': 'Product removed from cart successfully.'}, status=status.HTTP_200_OK)
    
#     except CustomUser.DoesNotExist:
#         return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    
#     except Cart.DoesNotExist:
#         return Response({'error': 'Cart not found.'}, status=status.HTTP_404_NOT_FOUND)
    
#     except CartItem.DoesNotExist:
#         return Response({'error': 'Product not found in cart.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def delete_cart_item(request, user_id, product_id, price):
    try:
        user = CustomUser.objects.get(id=user_id)
        cart = Cart.objects.get(user=user)

        cart_item = CartItem.objects.get(cart=cart, product_id=product_id, price=price)
        cart_item.delete()

        return Response({'message': 'Product removed from cart successfully.'}, status=status.HTTP_200_OK)
    
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    except Cart.DoesNotExist:
        return Response({'error': 'Cart not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    except CartItem.DoesNotExist:
        return Response({'error': 'Matching product not found in cart.'}, status=status.HTTP_404_NOT_FOUND)
    
    except CartItem.MultipleObjectsReturned:
        return Response({'error': 'Multiple cart items found, refine query.'}, status=status.HTTP_400_BAD_REQUEST)



class AdminUserSignupView(APIView):
    def post(self, request):
        serializer = AdminUserSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Admin user created successfully"}, status=status.HTTP_201_CREATED)
        else:
            # Add this for debugging
            print("Serializer Errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class AdminLoginView(APIView):
#     def post(self, request):
#         serializer = AdminLoginSerializer(data=request.data)
#         if serializer.is_valid():
#             return Response(serializer.validated_data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class AdminLoginView(APIView):
#     def post(self, request):
#         serializer = AdminLoginSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.validated_data['user']  # assumes serializer returns 'user'

#             # Check if user is inactive
#             if not user.is_active:
#                 raise AuthenticationFailed(detail="User is inactive", code="user_inactive")

#             # Track session start
#             user.start_session()

#             return Response(serializer.validated_data, status=status.HTTP_200_OK)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminLoginView(APIView):
    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = AdminUser.objects.get(email=serializer.validated_data['email'])

            # Set active status here
            if not user.is_active:
                user.is_active = True
                user.save(update_fields=['is_active'])

            # Start session timestamp
            if hasattr(user, 'start_session'):
                user.start_session()

            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerListView(APIView):
    # permission_classes = [IsAdminUser]

    def get(self, request):
        users = CustomUser.objects.filter(is_staff=False).order_by("id")
        paginator = CustomPaginationMain()
        paginated_users = paginator.paginate_queryset(users, request, view=self)
        serializer = CustomUserFetchSerializer(paginated_users, many=True)
        return paginator.get_paginated_response(serializer.data)
    
class AdminLogoutView(APIView):
    def post(self, request):
        request.session.flush()  # Clears the session
        return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)
    

class CustomLogoutView(APIView):
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "User is not authenticated."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(pk=request.user.pk)
            user.end_session()  # Call the method from your CustomUser model
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        request.session.flush()  # Clear session

        return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)


# class ProductByEncodedView(APIView):
#     """
#     GET /api/products-encoded/<encoded>/
#     where <encoded> == btoa(f"{id}-{slug}")
#     """

#     def get(self, request, encoded, *args, **kwargs):
#         # 1) Decode Base64 back into "<id>-<slug>"
#         try:
#             decoded = base64.b64decode(encoded).decode('utf-8')
#             id_str, _ = decoded.split('-', 1)
#             product_id = int(id_str)
#         except (ValueError, base64.binascii.Error, UnicodeDecodeError):
#             return Response(
#                 {"success": False, "error": "Invalid or malformed token."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # 2) Fetch or 404
#         product = get_object_or_404(Product, pk=product_id)

#         # 3) Format exactly like your list view does
#         formatter = ProductListView()
#         # bypass pagination by sending a one-item list
#         formatted = formatter.format_product_data([product])
#         # format_product_data returns {"products": [...]}
#         return Response(
#             {"success": True, **formatted},
#             status=status.HTTP_200_OK
#         )



class ProductByEncodedView(APIView):
    """
    GET /api/products/<encoded>/
    where <encoded> == btoa(f"{id}-{slug}")
    """

    def get(self, request, encoded, *args, **kwargs):
        try:
            decoded = base64.b64decode(encoded).decode('utf-8')
            id_str, _ = decoded.split('-', 1)
            product_id = int(id_str)
        except (ValueError, base64.binascii.Error, UnicodeDecodeError):
            return Response(
                {"success": False, "error": "Invalid or malformed token."},
                status=status.HTTP_400_BAD_REQUEST
            )

        product = get_object_or_404(Product, pk=product_id)

        # Get all serving sizes related to this product
        serving_sizes = ProductServingSize.objects.filter(product=product)
        serving_sizes_data = ProductServingSizeSerializer(serving_sizes, many=True).data

        product_data = {
            "id": product.id,
            "name": product.name,
            "category": product.category.id if product.category else None,
            "status": product.status,
            "description": product.description,
            "ingredients": product.ingredients,
            "allergen_info": product.allergen_info,
            "price": product.price,
            "discount_price": product.discount_price,
            "stock_status": product.stock_status,
            "serving_size": product.serving_size,
            "serving_sizes": serving_sizes_data,
            "total_stock": product.total_stock,
            "reorder_level": product.reorder_level,
            "cake_size": product.cake_size,
            "flavor_variants": product.flavor_variants,
            "product_images": product.product_images_base64.split(',') if product.product_images_base64 else [],
            "calories": product.calories,
            "nutrition_facts": product.nutrition_facts,
            "tags": product.tags,
            "reviews": product.reviews,
            "related_products":product.related_products,
            "created_at": product.created_at,
            "updated_at": product.updated_at,
        }

        return Response({
            "success": True,
            "product": product_data
        }, status=status.HTTP_200_OK)


# class OrderCreateView(generics.CreateAPIView):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializers

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)\

import logging
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import Order
from .serializers import OrderSerializers

# Setup a logger
logger = logging.getLogger(__name__)

# class OrderCreateView(generics.CreateAPIView):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializers

#     def create(self, request, *args, **kwargs):
#         try:
#             # NO need to mutate
#             request_data = request.data.copy()  # Make a safe copy

#             serializer = self.get_serializer(data=request_data)
#             serializer.is_valid(raise_exception=True)
#             self.perform_create(serializer)
#             headers = self.get_success_headers(serializer.data)

#             return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

#         except ValidationError as e:
#             logger.warning(f"Validation error during order creation: {e.detail}")
#             return Response({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        
#         except Exception as e:
#             logger.error(f"Unexpected error during order creation: {str(e)}", exc_info=True)
#             return Response({'error': 'Something went wrong while creating the order.'},
#                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializers

    def create(self, request, *args, **kwargs):
        try:
            request_data = request.data.copy()

            serializer = self.get_serializer(data=request_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)

            # ✅ Fetch user info
            user_id = serializer.validated_data.get("user").id
            user = CustomUser.objects.get(id=user_id)

            # ✅ Build HTML email body
            html_message = f"""
                <h2>Order Confirmation</h2>
                <p>Hi {user.first_name},</p>
                <p>Your order has been placed successfully! We'll notify you once it's shipped.</p>
                <p><strong>Order ID:</strong> {serializer.data['id']}</p>
                <p><strong>Total Amount:</strong> ₹{serializer.data['total_amount']}</p>
                <br/>
                <p>Thanks for shopping with <strong>Pies & Thies</strong>!</p>
            """

            plain_message = strip_tags(html_message)

            # ✅ Send Email
            send_mail(
                subject="🧾 Your Pies & Thies Order Confirmation",
                message=plain_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=True  # Set to False if you want to debug errors
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        except ValidationError as e:
            logger.warning(f"Validation error during order creation: {e.detail}")
            return Response({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Unexpected error during order creation: {str(e)}", exc_info=True)
            return Response({'error': 'Something went wrong while creating the order.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateOrderStatusView(APIView):
    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
            order_status = request.data.get("order_status")
            payment_status = request.data.get("payment_status")

            if order_status:
                order.order_status = order_status

            if payment_status:
                order.payment_status = payment_status

            order.save()

            return Response({"message": "Order updated successfully"}, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class UserOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializers

    def get_queryset(self):
        logger.info("coming in api")
        
        encoded_user_id = self.kwargs.get('encoded_user_id')  # <--- Fix here!

        if not encoded_user_id:
            logger.warning("No encoded_user_id provided in URL.")
            return Order.objects.none()

        try:
            decoded_user_id = base64.b64decode(encoded_user_id).decode('utf-8')
            logger.info(f"Decoded user ID: {decoded_user_id}")
            return Order.objects.filter(user__id=decoded_user_id)
        except Exception as e:
            logger.error(f"Error decoding user ID: {str(e)}", exc_info=True)
            return Order.objects.none()
        
class OrderListView(generics.ListAPIView):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializers
    pagination_class = CustomPaginationMain  # <-- set your custom pagination here


class OrderDeleteView(APIView):
    def post(self, request, order_id, *args, **kwargs):
        if not order_id:
            logger.error("Order deletion failed: No order ID provided in URL.")
            return Response({"success": False, "message": "Order ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            order = Order.objects.get(id=order_id)
            order.delete()
            logger.info(f"Order {order_id} deleted successfully.")
            return Response({"success": True, "message": "Order deleted successfully."}, status=status.HTTP_200_OK)
        
        except Order.DoesNotExist:
            logger.error(f"Order deletion failed: Order with ID {order_id} does not exist.")
            return Response({"success": False, "message": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            logger.exception(f"Unexpected error occurred while deleting order {order_id}: {str(e)}")
            return Response({"success": False, "message": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer

class CouponRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer

from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from django.core.mail import EmailMessage
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

def send_email(subject, html_message, to_email):
    """
    Reusable function to send HTML email.
    """
    if not to_email:
        raise ValueError("Recipient email is required.")

    if not settings.EMAIL_HOST_USER:
        raise ImproperlyConfigured("EMAIL_HOST_USER is not configured.")

    email = EmailMessage(
        subject=subject,
        body=html_message,
        from_email=settings.EMAIL_HOST_USER,
        to=[to_email]
    )
    email.content_subtype = "html"  # This is the key part
    email.send()

class ForgotPasswordAPIView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)

            # Generate token and UID
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Construct reset URL
            reset_url = f"https://prajnabyparth.com/reset-password/{uid}/{token}/"

            # Email content
            subject = "🔒 Reset Your Pies & Thies Password"
            html_message = f"""
                <h2>Password Reset Requested</h2>
                <p>Hi {user.first_name},</p>
                <p>We received a request to reset your password. Click the link below to set a new one:</p>
                <a href="{reset_url}">Reset My Password</a>
                <p>If you didn't request this, you can safely ignore this email.</p>
            """
            plain_message = f"Reset link: {reset_url}"

            send_mail(subject, plain_message, settings.EMAIL_HOST_USER, [user.email], html_message=html_message)

            return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password

class ResetPasswordAPIView(APIView):
    def post(self, request):
        uidb64 = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("password")

        print(f" uidb64 {uidb64} token {token}")

        if not uidb64 or not token or not new_password:
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Decode the UID from base64
            # uid = urlsafe_base64_decode(uidb64).decode()
            user = CustomUser.objects.get(id=uidb64)

            # Validate the token
            if default_token_generator.check_token(user, token):
                # Update the password and save the user
                user.password = make_password(new_password)
                user.save()

                # Send a confirmation email
                subject = "Your Password has been Reset"
                html_message = f"""
                    <p>Hello { user.first_name } { user.last_name }</p>
                    <p>Your password has been successfully reset.</p>
                    <p>If you did not request this change, please contact support immediately.</p>
                """
                send_email(subject, html_message, user.email)

                return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            return Response({"error": "Invalid UID."}, status=status.HTTP_400_BAD_REQUEST)
        

class ProfileAndAddressesAPIView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/profile/    → returns user + addresses
    PUT  /api/profile/    → replace entire profile+addresses
    PATCH /api/profile/   → partial update of profile+addresses
    """
    serializer_class = UserWithAddressesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user