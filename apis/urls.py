from django.urls import path
from .views import *

urlpatterns = [
    path('categories/', CategoryCreateView.as_view(), name='category-create'),
    path('categories-list/', CategoryListView.as_view(), name='category-list'),
    path('categories/main/', main_categories, name='main-categories'),
    path("categories/<int:category_id>/", update_category, name="update-category"),
    path("categories/delete/<int:category_id>/", delete_category, name="delete_category"),
    path('products/create/', ProductCreateAPIView.as_view(), name='add-product'),
    path('products-list/', ProductListView.as_view(), name='product-list'),
    path("product/delete/<int:product_id>/", delete_product, name="delete_product"),
    path("product/<int:productId>/", update_product, name="update_product"),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('banners/', BannerCreateAPIView.as_view(), name='banner-create'),
    path('banner-list/', BannerListView.as_view(), name='banner-list'),
    path('banner/<uuid:pk>/delete/', BannerDeleteAPIView.as_view(), name='banner-delete'),
    path('banner/<uuid:banner_id>/', get_banner_by_id, name='get_banner_by_id'),
    path('banner/<uuid:pk>/update', update_banner, name='update_banner'),
    path('why-choose-us/create/', WhyChooseUsCreateAPIView.as_view(), name='why_choose_us_create'),
    path('why-choose-us/', WhyChooseUsListAPIView.as_view(), name='why_choose_us_list'),
    path('why-choose-us/delete/<str:pk>/', WhyChooseUsDeleteAPIView.as_view(), name='why_choose_us_delete'),
    path('why-choose-us/update/', update_why_choose_us, name='update_why_choose_us'),
    path('top-pick-background/', TopPickBackgroundCreateView.as_view(), name='top_pick_background_create'),
    path('top-pick-background/list/', TopPickBackgroundListView.as_view(), name='top-pick-background-list'),
    path('top-pick-background/delete/<str:encoded_id>/', TopPickBackgroundDeleteView.as_view(), name='top-pick-delete'),
    path('top-pick-background/update/', update_top_pick, name='update_top_pick'),
    path('adds/', AddCreateAPIView.as_view(), name='add-create'),
    path('ads-list/', AdsListView.as_view(), name='add-list'),
    path('ads/<uuid:pk>/delete/', AddsDeleteAPIView.as_view(), name='adds-delete'),
    path('ads/<uuid:id>/', get_ads_by_id, name='get_ads_by_id'),
    path('ads/<uuid:pk>/update/', ads_banner, name='ads_banner'),
    path('baked-delights/create/', BakedDelightsCreateAPIView.as_view(), name='baked_delights'),
    path('baked-delights/list/', BakedDelightListAPIView.as_view(), name='baked_delight_list'),
    path('baked-delight/delete/<str:pk>/', BakedDelightDeleteAPIView.as_view(), name='baked_delight_delete'),
    path('baked-delight/update/', update_baked_delights, name='update_baked_delights'),
    path('add-to-cart/', add_to_cart, name='add_to_cart'),
    path('view-cart/<int:user_id>/', view_cart, name='view-cart'),
    path('admin/signup/', AdminUserSignupView.as_view(), name='admin-signup'),
    path('admin/login/', AdminLoginView.as_view(), name='admin-login'),
    path('admin/customers/', CustomerListView.as_view(), name='customer-list'),
    path('admin/logout/', AdminLogoutView.as_view(), name='admin-logout'),
    path('custom/logout/', CustomLogoutView.as_view(), name='custom-logout'),
    path(
        'products/<str:encoded>/',
        ProductByEncodedView.as_view(),
        name='product-by-encoded'
    ),
    path('cart/<int:user_id>/item/<int:product_id>/<str:price>/delete/', delete_cart_item, name='delete_cart_item'),
    path('orders/create/', OrderCreateView.as_view(), name='order-create'),
    path('orders/my-orders/<encoded_user_id>', UserOrderListView.as_view(), name='user-orders'),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/<int:order_id>/delete/', OrderDeleteView.as_view(), name='order-delete'),
    path('coupons/', CouponViewSet.as_view({'get': 'list', 'post': 'create'}), name='coupon-list-create'),
    path('coupons/<int:pk>/', CouponRetrieveUpdateDestroyAPIView.as_view(), name='coupon-detail'),
    path('orders/<int:pk>/update-status/', UpdateOrderStatusView.as_view(), name='update-order-status'),
    # path('send-email/', SendEmailAPIView.as_view(), name='send_email'),
    path('forgot-password/', ForgotPasswordAPIView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordAPIView.as_view(), name='reset_password'),
    path('profile/', ProfileAndAddressesAPIView.as_view(), name='profile-full-update'),
]
