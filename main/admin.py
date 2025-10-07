from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User,
    UserProfile,
    Brand,
    Product,
    ProductImage,
    Like,
    OrderProduct
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'username', 'email', 'is_verified', 'is_active', 'joined_at')
    list_filter = ('is_verified', 'is_active', 'joined_at')
    search_fields = ('username', 'email')
    ordering = ('-joined_at',)
    readonly_fields = ('joined_at',)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Status', {'fields': ('is_verified', 'joined_at')}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'phone', 'birth_date', 'telegram')
    search_fields = ('user__username', 'phone', 'telegram')
    list_filter = ('birth_date',)
    ordering = ('user__username',)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)
    readonly_fields = ('created_at',)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'brand', 'price', 'stock', 'is_available', 'created_at')
    list_filter = ('brand', 'is_available', 'created_at')
    search_fields = ('name', 'brand__name')
    ordering = ('-created_at',)
    inlines = [ProductImageInline]


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'product__name')
    ordering = ('-created_at',)


@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'product__name')
    ordering = ('-created_at',)
    readonly_fields = ('total_price', 'created_at')
