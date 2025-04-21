import base64
from django.core.files.base import ContentFile
from rest_framework import serializers
from .models import Category, Product, TopPickBackground
from .models import *
from django.utils.timezone import localtime

class CategorySerializer(serializers.ModelSerializer):
    image_base64 = serializers.CharField(write_only=True, required=False)  # Accept Base64 input
    image_file = serializers.ImageField(write_only=True, required=False)  # Accept file upload
    image_base64_output = serializers.SerializerMethodField()  # Return Base64 in response

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent', 'image_file', 'image_base64', 'image_base64_output', 'status', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_image_base64_output(self, obj):
        """Convert stored image file to Base64 for response"""
        if obj.image_base64:  
            return obj.image_base64  # Return stored Base64 if available
        elif obj.image:  
            try:
                with open(obj.image.path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode("utf-8")
            except Exception:
                return None
        return None

    def create(self, validated_data):
        """Handle Base64 image & file upload, store as Base64"""
        image_base64 = validated_data.pop('image_base64', None)
        image_file = validated_data.pop('image_file', None)

        if image_base64:
            # Ensure valid Base64
            try:
                base64.b64decode(image_base64.split(",")[-1])
            except Exception:
                raise serializers.ValidationError({"image_base64": "Invalid Base64 format."})
        
        elif image_file:
            # Convert image file to Base64
            try:
                image_content = image_file.read()
                image_base64 = base64.b64encode(image_content).decode("utf-8")
            except Exception:
                raise serializers.ValidationError({"image_file": "Error converting file to Base64."})

        validated_data['image_base64'] = image_base64
        return Category.objects.create(**validated_data)


class ProductSerializer(serializers.ModelSerializer):
    product_images_base64 = serializers.CharField(write_only=True, required=False)  # Accept Base64 input
    image_file = serializers.ListField(
        child=serializers.ImageField(write_only=True, required=False), required=False
    )  # Accept multiple file uploads
    product_images_base64_output = serializers.SerializerMethodField()  # Return Base64 in response
    # category = CategorySerializer(read_only=True)
    # category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'category_id', 'description', 'ingredients', 'allergen_info',
                  'price', 'discount_price', 'stock_status', 'serving_size', 'total_stock', 'reorder_level',
                  'weight', 'cake_size', 'flavor_variants', 'add_ons', 'image_file', 'product_images_base64',
                  'product_images_base64_output', 'calories', 'nutrition_facts', 'prep_time', 'delivery_option',
                  'shelf_life', 'tags', 'reviews', 'related_products', 'total_sales', 'status', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_product_images_base64_output(self, obj):
        """Convert stored images to Base64 for response"""
        if obj.product_images_base64:
            return obj.product_images_base64  # Return stored Base64 if available
        return None

    def create(self, validated_data):
        """Handle Base64 image & file upload, store as Base64"""
        product_images_base64 = validated_data.pop('product_images_base64', None)
        image_files = validated_data.pop('image_file', [])
        
        if product_images_base64:
            try:
                base64.b64decode(product_images_base64.split(",")[-1])
            except Exception:
                raise serializers.ValidationError({"product_images_base64": "Invalid Base64 format."})
        elif image_files:
            try:
                image_content = b"".join([img.read() for img in image_files])
                product_images_base64 = base64.b64encode(image_content).decode("utf-8")
            except Exception:
                raise serializers.ValidationError({"image_file": "Error converting file to Base64."})
        
        validated_data['product_images_base64'] = product_images_base64
        return Product.objects.create(**validated_data)


from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = (
            'first_name', 'last_name', 'email', 'phone',
            'password', 'confirm_password'
        )

    def validate(self, attrs):
        # Check if passwords match
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({"message": "Passwords do not match."})
        
        # Check if email already exists
        if CustomUser.objects.filter(email=attrs.get('email')).exists():
            raise serializers.ValidationError({"message": "Email already registered."})
        
        # Check if phone already exists
        if CustomUser.objects.filter(phone=attrs.get('phone')).exists():
            raise serializers.ValidationError({"message": "Phone number already registered."})
        
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = CustomUser.objects.create_user(**validated_data)
        user.start_session()  # Optional: auto-login logic
        return user

from rest_framework import serializers
from .models import Banner

class BannerSerializer(serializers.ModelSerializer):
    
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = Banner
        fields = ['id', 'heading', 'link', 'price', 'image', 'status', 'created_at', 'updated_at']

    def get_created_at(self, obj):
        return obj.created_at.strftime('%d-%m-%Y %H:%M:%S')

    def get_updated_at(self, obj):
        return obj.updated_at.strftime('%d-%m-%Y %H:%M:%S')
    
from .models import WhyChooseUs

class WhyChooseUsSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = WhyChooseUs
        fields = '__all__'

    def get_created_at(self, obj):
        return localtime(obj.created_at).strftime('%B %d, %Y, %I:%M %p')

    def get_updated_at(self, obj):
        return localtime(obj.updated_at).strftime('%B %d, %Y, %I:%M %p')
    
from rest_framework import serializers
from .models import TopPickBackground
import base64
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO

class TopPickBackgroundSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = TopPickBackground
        fields = '__all__'

    def get_created_at(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %I:%M %p') if obj.created_at else None

    def get_updated_at(self, obj):
        return obj.updated_at.strftime('%Y-%m-%d %I:%M %p') if obj.updated_at else None
    

class AdsSerializer(serializers.ModelSerializer):
    
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = Adds
        fields = ['id', 'heading', 'link', 'image', 'status', 'created_at', 'updated_at']

    def get_created_at(self, obj):
        return obj.created_at.strftime('%d-%m-%Y %H:%M:%S')

    def get_updated_at(self, obj):
        return obj.updated_at.strftime('%d-%m-%Y %H:%M:%S')
    
class BakedDelightsSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = BakedDelight
        fields = '__all__'

    def get_created_at(self, obj):
        return localtime(obj.created_at).strftime('%B %d, %Y, %I:%M %p')

    def get_updated_at(self, obj):
        return localtime(obj.updated_at).strftime('%B %d, %Y, %I:%M %p')
    
class CartSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'products', 'created_at', 'updated_at']

    def create(self, validated_data):
        user = validated_data.get('user')
        products_data = validated_data.get('products', [])
        
        cart = Cart.objects.create(user=user)
        cart.products.set([product['id'] for product in products_data])  # Associate products with the cart
        return cart

    def update(self, instance, validated_data):
        instance.products.clear()  # Clear current products
        instance.products.set([product['id'] for product in validated_data.get('products', [])])  # Update products
        instance.save()
        return instance
    
from .models import AdminUser

class AdminUserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = AdminUser
        fields = ['name', 'email', 'password']

    def create(self, validated_data):
        return AdminUser.objects.create_user(**validated_data)
    

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from .models import AdminUser

class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
            admin = AdminUser.objects.get(email=email)
        except AdminUser.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials or not an admin.")

        if not check_password(password, admin.password):
            raise serializers.ValidationError("Invalid credentials or not an admin.")

        refresh = RefreshToken.for_user(admin)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'admin_id': admin.id,
            'name': admin.name,
            'email': admin.email,
        }


class CustomUserFetchSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone',
            'first_login', 'session_started_at', 'session_ended_at',
            'created_at', 'updated_at', 'is_active'
        ]