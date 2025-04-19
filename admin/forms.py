from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name", "category", "price", "discount_price", "description",
            "ingredients", "allergens", "stock", "serving_size", "weight",
            "customization_options", "calories_per_serving", "preparation_time",
            "delivery_available", "shelf_life", "image", "tags"
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "ingredients": forms.Textarea(attrs={"rows": 3}),
            "customization_options": forms.Textarea(attrs={"rows": 2}),
            "tags": forms.TextInput(attrs={"placeholder": "E.g., Vegan, Gluten-free"}),
            "price": forms.NumberInput(attrs={"step": "0.01"}),
            "discount_price": forms.NumberInput(attrs={"step": "0.01"}),
            "calories_per_serving": forms.TextInput(attrs={"placeholder": "E.g., 250 kcal"}),
            "shelf_life": forms.TextInput(attrs={"placeholder": "E.g., Best consumed within 2 days"}),
        }
