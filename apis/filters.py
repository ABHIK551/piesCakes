import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr='icontains')
    category = django_filters.CharFilter(field_name="category__name", lookup_expr='icontains')
    price = django_filters.NumberFilter(field_name="price")
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    stock_status = django_filters.ChoiceFilter(choices=Product.STOCK_STATUS)
    delivery_option = django_filters.ChoiceFilter(choices=Product.DELIVERY_OPTIONS)
    total_stock = django_filters.NumberFilter(field_name="total_stock")
    min_stock = django_filters.NumberFilter(field_name="total_stock", lookup_expr='gte')
    max_stock = django_filters.NumberFilter(field_name="total_stock", lookup_expr='lte')
    status = django_filters.BooleanFilter(field_name="status")
    created_at = django_filters.DateTimeFilter(field_name="created_at")
    updated_at = django_filters.DateTimeFilter(field_name="updated_at")

    class Meta:
        model = Product
        fields = '__all__'