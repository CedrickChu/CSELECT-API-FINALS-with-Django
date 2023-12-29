from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import NewUser, CartItem, Status, Order, OrderDetail, Product, Cart, UserProfile


class CustomUserAdmin(UserAdmin):
    model = NewUser
    list_display = ['email', 'username', 'phone', 'is_active', 'is_staff']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'phone', 'first_name', 'about')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'start_date')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'phone', 'password1', 'password2'),
        }),
    )
    search_fields = ['email', 'username', 'phone']
    ordering = ['email']

admin.site.register(NewUser, CustomUserAdmin)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'cart', 'quantity']

    def product(self, obj):
        return obj.product.product_name

    product.short_description = 'Product'

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'status_name')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order_date', 'status', 'total_amount')

@admin.register(OrderDetail)
class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ('order', 'cart_item', 'quantity', 'unit_price', 'status')

    def cart_item(self, obj):
        return obj.cart_item

    cart_item.short_description = 'Cart Item'
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_code', 'product_name', 'description', 'category', 'price', 'quantity', 'display_image')

    def display_image(self, obj):
        return obj.display_image()

    display_image.short_description = 'Image'
    
class CartItemInline(admin.TabularInline):
    model = Cart.items.through
    extra = 1

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'id')
    inlines = [CartItemInline]

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'address', 'city', 'country', 'postal_code', 'about_me', 'profile_image')
