"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from store.views import ClothesViewSet, UserView, CartItemViewSet, UserRegister, index, search, itemcart, userItems

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

router = DefaultRouter()
router.register(r'clothes', ClothesViewSet, basename='clothes')
router.register(r'users', UserView, basename='users')
router.register(r'cartItem', CartItemViewSet, basename='cartItem')
router.register(r'register', UserRegister, basename='register')

urlpatterns = [
    path('', index),
    path('search.html/', search),
    path('admin/', admin.site.urls),
    path('cart.html/', itemcart),
    path('userItems.html', userItems),
    # path('clothes/<str:type>', clothes_view),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_URL)
