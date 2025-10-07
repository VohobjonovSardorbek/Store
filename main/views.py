from rest_framework import generics, permissions, status, viewsets, views
from .serializer import *
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "message": "Foydalanuvchi muvaffaqiyatli ro'yxatdan o'tdi.",
            "user": self.get_serializer(user).data
        }, status=status.HTTP_201_CREATED)


class ProfileAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = self.request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        return profile


class ProductListAPIView(generics.ListAPIView):
    serializer_class = ProductSafeSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Product.objects.all()


class MyProductListAPIView(generics.ListAPIView):
    serializer_class = ProductSafeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Product.objects.none()

        return Product.objects.filter(user=user)


class ProductCreateAPIView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Product.objects.all()


class ProductRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = ProductSafeSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Product.objects.all()


class ProductUpdateAPIView(generics.UpdateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Product.objects.none()

        return Product.objects.filter(user=user)


class ProductDeleteAPIView(generics.DestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Product.objects.none()

        return Product.objects.filter(user=user)


class ProductImageViewSet(viewsets.ModelViewSet):
    """
    Savdo platformasi uchun ProductImage ViewSet
    - Har kim ro'yxat va detallarni ko'ra oladi
    - Faqat mahsulot egasi create, update, delete qila oladi
    """
    queryset = ProductImage.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ProductImageSafeSerializer
        return ProductImageSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [perm() for perm in permission_classes]

    def get_queryset(self):
        """
        - list va retrieve: hamma ko‘ra oladi
        - update, delete, create: faqat egasiga tegishli product image’lar
        """
        user = self.request.user
        if self.action in ['list', 'retrieve']:
            return ProductImage.objects.all()
        if user.is_authenticated:
            return ProductImage.objects.filter(product__user=user)
        return ProductImage.objects.none()


class LikeListAPIView(generics.ListAPIView):
    serializer_class = LikeSafeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Like.onjects.none()
        return Like.objects.filter(user=user)


class LikeToggleAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'product_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Mahsulot ID si')
            },
            required=['product_id']
        ),
        responses={200: 'Like toggled successfully'}
    )

    def post(self, request, *args, **kwargs):
        serializer = LikeToggleSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        result = serializer.toggle_like()
        return Response(result, status=status.HTTP_200_OK)


class OrderProductListAPIView(generics.ListAPIView):
    serializer_class = OrderProductSafeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return OrderProduct.objects.none()
        return OrderProduct.objects.filter(user=user).order_by('-created_at')


class OrderProductCreateAPIView(generics.CreateAPIView):
    serializer_class = OrderProductCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderProductRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = OrderProductSafeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return OrderProduct.objects.none()
        return OrderProduct.objects.filter(user=user)


class OrderProductUpdateAPIView(generics.UpdateAPIView):
    serializer_class = OrderProductUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return OrderProduct.objects.none()
        return OrderProduct.objects.filter(user=user)


class OrderProductDeleteAPIView(generics.DestroyAPIView):
    serializer_class = OrderProductSafeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return OrderProduct.objects.none()
        return OrderProduct.objects.filter(user=user)
