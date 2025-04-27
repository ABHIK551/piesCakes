from django.db import models
from django.utils.timezone import now
from django.utils import timezone

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone




class CustomUserManager(BaseUserManager):
    def create_user(self, email, phone, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field is required')
        if not phone:
            raise ValueError('The Phone field is required')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, phone, first_name, last_name, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    # Personal Info
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)

    # Session Tracking
    first_login = models.DateTimeField(null=True, blank=True)
    session_started_at = models.DateTimeField(null=True, blank=True)
    session_ended_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Permissions
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def start_session(self):
        now = timezone.now()
        self.session_started_at = now
        if not self.first_login:
            self.first_login = now
        self.save()

    def end_session(self):
        self.session_ended_at = timezone.now()
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name="subcategories")
    image = models.ImageField(null=True, blank=True)  # Image upload support (optional)
    image_base64 = models.TextField(null=True, blank=True)  # Base64 storage
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    STOCK_STATUS = [
        ('in_stock', 'In Stock'),
        ('out_of_stock', 'Out of Stock'),
    ]
    
    DELIVERY_OPTIONS = [
        ('pickup', 'In-store Pickup'),
        ('home_delivery', 'Home Delivery'),
    ]
    
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    ingredients = models.TextField(blank=True, null=True)
    allergen_info = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock_status = models.CharField(max_length=20, choices=STOCK_STATUS, default='in_stock')
    serving_size = models.CharField(max_length=50, blank=True, null=True)
    total_stock = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=0)
    weight = models.CharField(max_length=50, blank=True, null=True)
    cake_size = models.CharField(max_length=20, blank=True, null=True)
    flavor_variants = models.CharField(max_length=255, blank=True, null=True)
    add_ons = models.CharField(max_length=255, blank=True, null=True)
    product_images_base64 = models.TextField(blank=True, null=True)
    calories = models.CharField(max_length=50, blank=True, null=True)
    nutrition_facts = models.TextField(blank=True, null=True)
    prep_time = models.CharField(max_length=50, blank=True, null=True)
    delivery_option = models.CharField(max_length=20, choices=DELIVERY_OPTIONS, blank=True, null=True)
    shelf_life = models.CharField(max_length=50, blank=True, null=True)
    tags = models.CharField(max_length=255, blank=True, null=True)
    reviews = models.TextField(blank=True, null=True)
    related_products = models.CharField(max_length=255, blank=True, null=True)
    total_sales = models.PositiveIntegerField(default=0)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    


import uuid
from django.db import models

class Banner(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    heading = models.CharField(max_length=255)
    link = models.URLField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.heading
    
class WhyChooseUs(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.TextField()  # Base64 encoded image string
    heading = models.CharField(max_length=255)
    description = models.TextField()
    status = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.heading
    
class TopPickBackground(models.Model):
    STATUS_CHOICES = [
        ('1', 'Active'),
        ('2', 'Inactive'),
    ]
    image = models.TextField()  # Changed from ImageField
    link = models.URLField(max_length=500)
    heading = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='1',
    )    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # NEW FIELD

    def __str__(self):
        return self.heading
    
class Adds(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    heading = models.CharField(max_length=255)
    link = models.URLField()
    image = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.heading
    
class BakedDelight(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.TextField()  # Base64 encoded image string
    heading = models.CharField(max_length=255)
    description = models.TextField()
    link = models.URLField(max_length=500)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.heading

class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    # products = models.ManyToManyField(Product, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set when the cart is created
    updated_at = models.DateTimeField(auto_now=True)     # Automatically set to the current time when the cart is updated

    def __str__(self):
        return f"Cart for {self.user.username}"
    
    def get_total_price(self):
        total = 0
        for product in self.products.all():
            total += product.discount_price if product.discount_price else product.price
        return total

class CartItem(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group, Permission
from django.db import models

class AdminUserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError("Admins must have an email address")
        email = self.normalize_email(email)
        admin = self.model(email=email, name=name)
        admin.set_password(password)
        admin.save(using=self._db)
        return admin

    def create_superuser(self, email, name, password=None):
        admin = self.create_user(email, name, password)
        admin.is_superuser = True
        admin.is_staff = True
        admin.save(using=self._db)
        return admin

class AdminUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    groups = models.ManyToManyField(
        Group,
        related_name='adminuser_set',  # 👈 Fix for groups
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='adminuser_set',  # 👈 Fix for permissions
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = AdminUserManager()

    def __str__(self):
        return self.emails
    
class Order(models.Model):

    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('online', 'Online Payment'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    delivery_address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=1)  # Example: setting the default product by ID    quantity = models.PositiveIntegerField()
    item_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2)


    def __str__(self):
        return f"Item in Order #{self.order.id}"