import base64
from django.core.files.base import ContentFile
from rest_framework import serializers
from .models import Category, Product, TopPickBackground
from .models import *
from django.utils.timezone import localtime
import json

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



# class ProductSerializer(serializers.ModelSerializer):
#     product_images_base64 = serializers.CharField(write_only=True, required=False)  # Accept Base64 input
#     image_file = serializers.ListField(
#         child=serializers.ImageField(write_only=True, required=False), required=False
#     )  # Accept multiple file uploads
#     product_images_base64_output = serializers.SerializerMethodField()  # Return Base64 in response
#     # category = CategorySerializer(read_only=True)
#     # category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True)

#     class Meta:
#         model = Product
#         fields = ['id', 'name', 'category', 'category_id', 'description', 'ingredients', 'allergen_info',
#                   'price', 'discount_price', 'stock_status', 'serving_size', 'total_stock', 'reorder_level',
#                   'weight', 'cake_size', 'flavor_variants', 'add_ons', 'image_file', 'product_images_base64',
#                   'product_images_base64_output', 'calories', 'nutrition_facts', 'prep_time', 'delivery_option',
#                   'shelf_life', 'tags', 'reviews', 'related_products', 'total_sales', 'status', 'created_at', 'updated_at']
#         read_only_fields = ['created_at', 'updated_at']

#     def get_product_images_base64_output(self, obj):
#         """Convert stored images to Base64 for response"""
#         if obj.product_images_base64:
#             return obj.product_images_base64  # Return stored Base64 if available
#         return None

#     def create(self, validated_data):
#         """Handle Base64 image & file upload, store as Base64"""
#         product_images_base64 = validated_data.pop('product_images_base64', None)
#         image_files = validated_data.pop('image_file', [])
        
#         if product_images_base64:
#             try:
#                 base64.b64decode(product_images_base64.split(",")[-1])
#             except Exception:
#                 raise serializers.ValidationError({"product_images_base64": "Invalid Base64 format."})
#         elif image_files:
#             try:
#                 image_content = b"".join([img.read() for img in image_files])
#                 product_images_base64 = base64.b64encode(image_content).decode("utf-8")
#             except Exception:
#                 raise serializers.ValidationError({"image_file": "Error converting file to Base64."})
        
#         validated_data['product_images_base64'] = product_images_base64
#         return Product.objects.create(**validated_data)

class ProductServingSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductServingSize
        fields = ['size', 'price', 'discount_price']


# class ProductSerializer(serializers.ModelSerializer):
#     # Input field for creating serving sizes
#     serving_sizes_input = ProductServingSizeSerializer(many=True, write_only=True, required=False)

#     # Output field for returning serving sizes
#     serving_sizes = ProductServingSizeSerializer(many=True, read_only=True)

#     # Image fields
#     product_images_base64 = serializers.CharField(write_only=True, required=False)
#     image_file = serializers.ListField(
#         child=serializers.ImageField(write_only=True, required=False),
#         required=False
#     )
#     product_images_base64_output = serializers.SerializerMethodField()

#     class Meta:
#         model = Product
#         fields = [
#             'id', 'name', 'category', 'category_id', 'description', 'ingredients', 'allergen_info',
#             'stock_status', 'total_stock', 'reorder_level',
#             'weight', 'cake_size', 'flavor_variants', 'add_ons',
#             'product_images_base64', 'image_file', 'product_images_base64_output',
#             'calories', 'nutrition_facts', 'prep_time', 'delivery_option',
#             'shelf_life', 'tags', 'reviews', 'related_products',
#             'total_sales', 'status', 'created_at', 'updated_at',
#             'serving_sizes_input',  # Input only
#             'serving_sizes'         # Output only
#         ]
#         read_only_fields = ['created_at', 'updated_at']

#     def get_product_images_base64_output(self, obj):
#         if obj.product_images_base64:
#             return obj.product_images_base64.split(',')  # Return list of base64 strings
#         return []

#     def create(self, validated_data):
#         serving_sizes_data = validated_data.pop('serving_sizes_input', [])
#         product_images_base64 = validated_data.pop('product_images_base64', None)
#         image_files = validated_data.pop('image_file', [])
#         print("Serving Sizes Input Received:", serving_sizes_data)

#         # If base64 not provided, convert image files to base64
#         if not product_images_base64 and image_files:
#             try:
#                 image_base64_list = []
#                 for img in image_files:
#                     image_base64_list.append(base64.b64encode(img.read()).decode("utf-8"))
#                 product_images_base64 = ",".join(image_base64_list)
#             except Exception:
#                 raise serializers.ValidationError({"image_file": "Error converting image to Base64."})

#         validated_data['product_images_base64'] = product_images_base64
#         product = Product.objects.create(**validated_data)

#         for size_data in serving_sizes_data:
#             print("Creating Serving Size:", size_data, " for ", product)
#             ProductServingSize.objects.create(product=product, **size_data)

#         # Ensure reverse relations like .serving_sizes are updated
#         product.refresh_from_db()

#         return product

# class ProductSerializer(serializers.ModelSerializer):
#     serving_sizes_input = ProductServingSizeSerializer(many=True, write_only=True, required=False)
#     serving_sizes = ProductServingSizeSerializer(many=True, read_only=True)

#     product_images_base64 = serializers.CharField(write_only=True, required=False)
#     image_file = serializers.ListField(
#         child=serializers.ImageField(write_only=True, required=False),
#         required=False
#     )
#     product_images_base64_output = serializers.SerializerMethodField()

#     class Meta:
#         model = Product
#         fields = [
#             'id', 'name', 'category', 'category_id', 'description', 'ingredients', 'allergen_info',
#             'stock_status', 'total_stock', 'reorder_level',
#             'weight', 'cake_size', 'flavor_variants', 'add_ons',
#             'product_images_base64', 'image_file', 'product_images_base64_output',
#             'calories', 'nutrition_facts', 'prep_time', 'delivery_option',
#             'shelf_life', 'tags', 'reviews', 'related_products',
#             'total_sales', 'status', 'created_at', 'updated_at',
#             'serving_sizes_input',  # input only
#             'serving_sizes'         # output only
#         ]
#         read_only_fields = ['created_at', 'updated_at']

#     def validate_serving_sizes_input(self, value):
#         for item in value:
#             if 'size' not in item or 'price' not in item:
#                 raise serializers.ValidationError("Each serving size must include 'size' and 'price'.")
#         return value

#     def get_product_images_base64_output(self, obj):
#         return obj.product_images_base64.split(',') if obj.product_images_base64 else []

#     def create(self, validated_data):
#         serving_sizes_data = validated_data.pop('serving_sizes_input', [])
#         product_images_base64 = validated_data.pop('product_images_base64', None)
#         image_files = validated_data.pop('image_file', [])
#         print("Serving Sizes Input Received:", serving_sizes_data)

#         if not product_images_base64 and image_files:
#             try:
#                 image_base64_list = []
#                 for img in image_files:
#                     image_base64_list.append(base64.b64encode(img.read()).decode("utf-8"))
#                 product_images_base64 = ",".join(image_base64_list)
#             except Exception:
#                 raise serializers.ValidationError({"image_file": "Error converting image to Base64."})

#         validated_data['product_images_base64'] = product_images_base64
#         product = Product.objects.create(**validated_data)

#         for size_data in serving_sizes_data:
#             print("Creating Serving Size:", size_data, " for ", product)
#             ProductServingSize.objects.create(product=product, **size_data)

#         product.refresh_from_db()
#         return product


class ProductSerializer(serializers.ModelSerializer):
    serving_sizes_input = ProductServingSizeSerializer(many=True, write_only=True, required=False)
    serving_sizes = ProductServingSizeSerializer(many=True, read_only=True)

    product_images_base64 = serializers.CharField(write_only=True, required=False)
    image_file = serializers.ListField(
        child=serializers.ImageField(write_only=True, required=False),
        required=False
    )
    product_images_base64_output = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'category_id', 'description', 'ingredients', 'allergen_info',
            'stock_status', 'total_stock', 'reorder_level',
            'weight', 'cake_size', 'flavor_variants', 'add_ons',
            'product_images_base64', 'image_file', 'product_images_base64_output',
            'calories', 'nutrition_facts', 'prep_time', 'delivery_option',
            'shelf_life', 'tags', 'reviews', 'related_products',
            'total_sales', 'status', 'created_at', 'updated_at',
            'serving_sizes_input',  # input only
            'serving_sizes'         # output only
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_serving_sizes_input(self, value):
        for item in value:
            if 'size' not in item or 'price' not in item:
                raise serializers.ValidationError("Each serving size must include 'size' and 'price'.")
        return value

    def get_product_images_base64_output(self, obj):
        return obj.product_images_base64.split(',') if obj.product_images_base64 else []

    def create(self, validated_data):
        serving_sizes_data = validated_data.pop('serving_sizes_input', [])
        product_images_base64 = validated_data.pop('product_images_base64', None)
        image_files = validated_data.pop('image_file', [])
        print("Serving Sizes Input Received:", serving_sizes_data)

        if not product_images_base64 and image_files:
            try:
                image_base64_list = []
                for img in image_files:
                    image_base64_list.append(base64.b64encode(img.read()).decode("utf-8"))
                product_images_base64 = ",".join(image_base64_list)
            except Exception:
                raise serializers.ValidationError({"image_file": "Error converting image to Base64."})

        validated_data['product_images_base64'] = product_images_base64
        product = Product.objects.create(**validated_data)

        for size_data in serving_sizes_data:
            print("Creating Serving Size:", size_data, " for ", product)
            ProductServingSize.objects.create(product=product, **size_data)

        product.refresh_from_db()
        return product

    def update(self, instance, validated_data):
        serving_sizes_data = validated_data.pop('serving_sizes_input', None)
        product_images_base64 = validated_data.pop('product_images_base64', None)
        image_files = validated_data.pop('image_file', [])

        # Convert image file to base64 if present
        if not product_images_base64 and image_files:
            try:
                image_base64_list = []
                for img in image_files:
                    image_base64_list.append(base64.b64encode(img.read()).decode("utf-8"))
                product_images_base64 = ",".join(image_base64_list)
            except Exception:
                raise serializers.ValidationError({"image_file": "Error converting image to Base64."})

        if product_images_base64:
            validated_data['product_images_base64'] = product_images_base64

        instance = super().update(instance, validated_data)

        if serving_sizes_data is not None:
            instance.serving_sizes.all().delete()
            for size_data in serving_sizes_data:
                ProductServingSize.objects.create(product=instance, **size_data)

        instance.refresh_from_db()
        return instance



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
    
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = ['product', 'quantity', 'size', 'price', 'discount_price']  

class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'cart_items', 'created_at', 'updated_at']

    def create(self, validated_data):
        user = validated_data.get('user')
        cart_items_data = validated_data.pop('cart_items', [])

        cart = Cart.objects.create(user=user)
        for item in cart_items_data:
            CartItem.objects.create(cart=cart, **item)
        return cart

    def update(self, instance, validated_data):
        instance.cart_items.all().delete()  # Clear old items
        cart_items_data = validated_data.pop('cart_items', [])

        for item in cart_items_data:
            CartItem.objects.create(cart=instance, **item)
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
    first_login = serializers.DateTimeField(format="%d %b %Y, %I:%M %p", required=False, allow_null=True)
    session_started_at = serializers.DateTimeField(format="%d %b %Y, %I:%M %p", required=False, allow_null=True)
    session_ended_at = serializers.DateTimeField(format="%d %b %Y, %I:%M %p", required=False, allow_null=True)
    created_at = serializers.DateTimeField(format="%d %b %Y, %I:%M %p", required=False, allow_null=True)
    updated_at = serializers.DateTimeField(format="%d %b %Y, %I:%M %p", required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone',
            'first_login', 'session_started_at', 'session_ended_at',
            'created_at', 'updated_at', 'is_active'
        ]

# serializers.py

# class OrderItemSerializer(serializers.ModelSerializer):
#     product_id = serializers.IntegerField(source='product.id', read_only=True)
#     product_name = serializers.CharField(source='product.name', read_only=True)

#     class Meta:
#         model = OrderItem
#         fields = ['product_id', 'product_name', 'quantity', 'item_price', 'discount', 'total']

class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product_id', 'product_name', 'quantity', 'item_price', 'discount', 'total']



class OrderSerializers(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()  # Add separate field for user full name
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'user_name', 'order_items', 'delivery_address', 'city', 'state', 'pincode',
            'phone_number', 'payment_method', 'payment_status', 'transaction_id',
            'coupon_code', 'discount_amount', 'total_amount', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user else None

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')
        order = Order.objects.create(**validated_data)
        for item_data in order_items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'