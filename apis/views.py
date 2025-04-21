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


class ProductCreateAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request, *args, **kwargs):
        data = request.data.copy()

        if 'product_images' in request.FILES:
            image_files = request.FILES.getlist('product_images')
            image_base64_list = []

            for image_file in image_files:
                try:
                    image_content = image_file.read()  # Read file content
                    encoded_image = base64.b64encode(image_content).decode("utf-8")
                    image_base64_list.append(encoded_image)
                except Exception as e:
                    return Response({
                        "success": False,
                        "message": f"Error processing image: {str(e)}"
                    }, status=status.HTTP_400_BAD_REQUEST)
                finally:
                    image_file.close()  # Explicitly close the file

            data['product_images_base64'] = ",".join(image_base64_list)

        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Product created successfully!"
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "message": "Failed to add product!",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def create(self, request, *args, **kwargs):
        # Extract request data
        data = request.data.dict() if isinstance(request.data, dict) else request.data.copy()
        print("Received Data:", data)  # Debugging

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
        # Apply filtering
        queryset = self.filter_queryset(self.get_queryset())

        # Paginate the results
        page = self.paginate_queryset(queryset)
        if page is not None:
            data = self.format_product_data(page)
            return self.get_paginated_response(data)

        # If pagination is disabled, return the full dataset
        data = self.format_product_data(queryset)
        return Response({"success": True, "products": data}, status=status.HTTP_200_OK)

    def format_product_data(self, queryset):
        """ Format products and include related category data """
        products = []

        for product in queryset:
            product_data = {
                "id": product.id,
                "name": product.name,
                "category": {
                    "id": product.category.id,
                    "name": product.category.name
                } if product.category else None,  # Include category info if available
                "description": product.description,
                "ingredients": product.ingredients,
                "allergen_info": product.allergen_info,
                "price": product.price,
                "discount_price": product.discount_price,
                "stock_status": product.stock_status,
                "serving_size": product.serving_size,
                "total_stock": product.total_stock,
                "reorder_level": product.reorder_level,
                "weight": product.weight,
                "cake_size": product.cake_size,
                "flavor_variants": product.flavor_variants,
                "add_ons": product.add_ons,
                "product_images": product.product_images_base64,
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


@api_view(["PUT", "PATCH", "POST"])
@parser_classes([MultiPartParser, FormParser])
def update_product(request, productId):
    product = get_object_or_404(Product, id=productId)
    data = request.data.copy()

    # Handle image upload (Convert to Base64)
    if "image" in request.FILES:
        image_file = request.FILES["image"]
        data["image_base64"] = base64.b64encode(image_file.read()).decode("utf-8")

    # Convert "Active" / "Inactive" to boolean
    if "status" in data:
        data["status"] = data["status"] == "Active"

    serializer = ProductSerializer(product, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
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
            return Response({"message": "Registration successful.", "status": "success"}, status=status.HTTP_201_CREATED)
        
        # Flatten errors
        error = serializer.errors.get("message") or next(iter(serializer.errors.values()))[0]
        return Response({"message": error, "status": "error"}, status=status.HTTP_400_BAD_REQUEST)

import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta

class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"success": False, "message": "Email and password required."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=email, password=password)

        if user is not None:
            # ✅ Generate JWT token
            payload = {
                "user_id": user.id,
                "email": user.email,
                "exp": datetime.utcnow() + timedelta(hours=2),  # Token expires in 2 hours
                "iat": datetime.utcnow()
            }
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

            return Response({
                "success": True,
                "message": "Login successful",
                "token": token,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": f"{user.first_name} {user.last_name}"
                }
            })
        else:
            return Response({"success": False, "message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

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
    print(data)
    
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
            print(f"top_pick_id {top_pick_id}")
            heading = request.POST.get('heading')
            print(f"heading {heading}")
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
        print(f"ads {ads}")
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
    print(data)
    
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
        print(request.body)
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
    
@api_view(['POST'])
def add_to_cart(request):
    if request.method == 'POST':
        # Extract userId and productIds from the request data
        user_id = request.data.get('userId')
        product_ids = request.data.get('productIds')

        # If productIds is not a list, convert it into one
        if isinstance(product_ids, int):  # If it's a single integer
            product_ids = [product_ids]
        elif not isinstance(product_ids, list):  # If it's neither a list nor a single integer
            return Response({'error': 'productIds should be a list or a single integer.'}, status=status.HTTP_400_BAD_REQUEST)

        if not user_id or not product_ids:
            return Response({'error': 'userId and productIds are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the user object
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Get the products
        products = Product.objects.filter(id__in=product_ids)

        # If no products were found with the given IDs
        if not products.exists():
            return Response({'error': 'Some products not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Get or create the user's cart
        cart, created = Cart.objects.get_or_create(user=user)

        # Add products to the cart
        cart.products.add(*products)
        cart.save()

        # Serialize the cart and return the response
        from .serializers import CartSerializer
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
@api_view(['GET'])
def view_cart(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        cart, created = Cart.objects.get_or_create(user=user)

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    
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

class AdminLoginView(APIView):
    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.permissions import IsAdminUser 

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