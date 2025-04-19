from django.db import models

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('cakes', 'Cakes'),
        ('cookies', 'Cookies'),
        ('breads', 'Breads'),
        ('pastries', 'Pastries'),
        ('others', 'Others'),
    ]

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    ingredients = models.TextField(blank=True, null=True)
    allergens = models.CharField(max_length=255, blank=True, null=True, help_text="E.g., Nuts, Dairy-Free, Gluten-Free")
    stock = models.PositiveIntegerField()
    serving_size = models.CharField(max_length=100, blank=True, null=True, help_text="E.g., Serves 4-6 people")
    weight = models.CharField(max_length=50, blank=True, null=True, help_text="E.g., 500g")
    customization_options = models.TextField(blank=True, null=True, help_text="E.g., Extra toppings, Special messages")
    calories_per_serving = models.CharField(max_length=50, blank=True, null=True)
    preparation_time = models.CharField(max_length=100, blank=True, null=True, help_text="E.g., 24 hours notice required")
    delivery_available = models.BooleanField(default=True)
    shelf_life = models.CharField(max_length=100, blank=True, null=True, help_text="E.g., Best consumed within 2 days")
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    tags = models.CharField(max_length=255, blank=True, null=True, help_text="E.g., Vegan, Eggless, Keto-friendly")
    created_at = models.DateTimeField(auto_now_add=True)