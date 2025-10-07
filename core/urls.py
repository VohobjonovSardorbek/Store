from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import token_obtain_pair, token_refresh
from rest_framework.routers import DefaultRouter
from django.contrib import admin
from django.urls import path
from main.views import *

router = DefaultRouter()
router.register(r'product-images', ProductImageViewSet, basename='productimage')

schema_view = get_schema_view(
    openapi.Info(
        title="Store API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="vohobjonovsardorbek@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

urlpatterns += [
    path('token/', token_obtain_pair),
    path('token/refresh/', token_refresh),
]

urlpatterns += [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('profile/', ProfileAPIView.as_view(), name='profile'),

    path('products/', ProductListAPIView.as_view(), name='product-list'),
    path('products/my/', MyProductListAPIView.as_view(), name='product-my'),
    path('products/create/', ProductCreateAPIView.as_view(), name='product-create'),
    path('products/<int:pk>/detail/', ProductRetrieveAPIView.as_view(), name='product-detail'),
    path('products/<int:pk>/update/', ProductUpdateAPIView.as_view(), name='product-update'),
    path('products/<int:pk>/delete/', ProductDeleteAPIView.as_view(), name='product-delete'),

    path('likes/', LikeListAPIView.as_view(), name='like-list'),
    path('likes/toggle/', LikeToggleAPIView.as_view(), name='like-toggle'),

    path('orders/', OrderProductListAPIView.as_view(), name='order-list'),
    path('orders/create/', OrderProductCreateAPIView.as_view(), name='order-create'),
    path('orders/<int:pk>/detail/', OrderProductRetrieveAPIView.as_view(), name='order-detail'),
    path('orders/<int:pk>/update/', OrderProductUpdateAPIView.as_view(), name='order-update'),
    path('orders/<int:pk>/delete/', OrderProductDeleteAPIView.as_view(), name='order-delete'),

]

urlpatterns += router.urls
