from django.urls import path, include
from django.contrib.auth.views import LoginView
from . import views
from rest_framework.routers import DefaultRouter
from .schema import schema
from graphene_django.views import GraphQLView
from django.contrib.auth import views as auth_views





from .views import (
    NewUserViewSet,
    StatusViewSet,
    ProductViewSet,
    OrderViewSet,
    CartItemViewSet,
)
router = DefaultRouter()
router.register(r'users', NewUserViewSet)
router.register(r'statuses', StatusViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'cart-items', CartItemViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('', LoginView.as_view(template_name='login.html'), name='login'),
    path('dashboard/', views.home_view, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.LogoutView.as_view(next_page='/'), name='logout'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('add_to_cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.view_cart, name='cart'),
    path('get_cart_data/', views.get_cart_data, name='get_cart_data'),
    path('profile/', views.update_profile, name='update_profile'),
]