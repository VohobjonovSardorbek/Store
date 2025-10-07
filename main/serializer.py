from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import *
from decimal import Decimal

User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'password',
            'email'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu email allaqachon ishlatilgan.")
        return value


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email'
        ]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', required=False)
    email = serializers.EmailField(source='user.email', required=False)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = UserProfile
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'image',
            'bio',
            'phone',
            'birth_date',
            'address',
            'telegram'
        ]
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user
        password = validated_data.pop('password', None)

        for attr, value in user_data.items():
            setattr(user, attr, value)
        if password:
            user.set_password(password)
        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = [
            'id',
            'name',
            'description',
            'logo',
        ]


class ProductSafeSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    brand = BrandSerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'user',
            'brand',
            'description',
            'ram',
            'color',
            'price',
            'stock',
            'is_available',
            'created_at',
            'updated_at'
        ]


class ProductSerializer(serializers.ModelSerializer):
    brand = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all())

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'brand',
            'description',
            'price',
            'stock',
            'is_available',
            'ram',
            'color',
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

    def validate_price(self, value):
        if value <= Decimal('0.00'):
            raise serializers.ValidationError("Narx musbat bo‘lishi kerak.")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Ombordagi miqdor manfiy bo‘lishi mumkin emas.")
        return value


class ProductShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
        ]


class ProductImageSafeSerializer(serializers.ModelSerializer):
    product = ProductShortSerializer(read_only=True)
    image = serializers.ImageField()

    class Meta:
        model = ProductImage
        fields = [
            'id',
            'product',
            'image',
        ]


class ProductImageSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    image = serializers.ImageField()

    class Meta:
        model = ProductImage
        fields = [
            'id',
            'product',
            'image',
        ]

    def validate_product(self, value):
        user = self.context['request'].user
        if value.user != user:
            raise serializers.ValidationError("Bu mahsulot sizga tegishli emas.")
        return value


class LikeSafeSerializer(serializers.ModelSerializer):
    product = ProductSafeSerializer(read_only=True)

    class Meta:
        model = Like
        fields = [
            'id',
            'product',
        ]


class LikeToggleSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Bunday mahsulot mavjud emas.")
        return value

    def toggle_like(self):
        user = self.context['request'].user
        product = Product.objects.get(id=self.validated_data['product_id'])

        like, created = Like.objects.get_or_create(user=user, product=product)
        if not created:
            like.delete()
            return {"product_id": product.id, "liked": False, "message": "Like olib tashlandi"}
        return {"product_id": product.id, "liked": True, "message": "Mahsulot yoqtirildi"}


class OrderProductSafeSerializer(serializers.ModelSerializer):
    product = ProductShortSerializer(read_only=True)

    class Meta:
        model = OrderProduct
        fields = [
            'id',
            'product',
            'quantity',
            'total_price',
            'status',
            'created_at',
        ]


class OrderProductCreateSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = OrderProduct
        fields = [
            'id',
            'product',
            'quantity',
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        total_price = validated_data['quantity'] * validated_data['product'].price
        validated_data['total_price'] = total_price
        validated_data['user'] = user
        return super().create(validated_data)


class OrderProductUpdateSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        required=False
    )
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = OrderProduct
        fields = [
            'id',
            'product',
            'quantity',
            'status',
            'total_price',
            'created_at',
        ]
        read_only_fields = ['id', 'total_price', 'user', 'created_at']

    def validate_quantity(self, value):
        if value is None:
            return value
        if value <= 0:
            raise serializers.ValidationError("Miqdor 1 dan katta bo'lishi kerak.")
        return value

    def validate_status(self, value):
        valid_choices = {choice[0] for choice in OrderProduct.STATUS_CHOICES}
        if value not in valid_choices:
            raise serializers.ValidationError("Noto'g'ri status qiymati.")
        return value

    def update(self, instance, validated_data):
        product = validated_data.get('product', instance.product)
        quantity = validated_data.get('quantity', instance.quantity)

        if quantity is None or quantity <= 0:
            raise serializers.ValidationError({"quantity": "Miqdor ijobiy butun son bo'lishi kerak."})

        total_price = product.price * Decimal(quantity)

        instance.product = product
        instance.quantity = quantity

        if 'status' in validated_data:
            instance.status = validated_data['status']

        instance.total_price = total_price
        instance.save()
        return instance
