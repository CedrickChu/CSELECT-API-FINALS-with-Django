from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.conf import settings




class CustomAccountManager(BaseUserManager):
    def create_user(self, email, username, phone, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, username, phone, password, **extra_fields)

class NewUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(max_length=150, blank=True, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,14}$', message="Phone number must be in the format: '+999999999'. Up to 14 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=15, unique=True)
    first_login = models.BooleanField(default=False)
    start_date = models.DateTimeField(default=timezone.now)
    about = models.TextField(_('about'), max_length=500, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone']
    
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to. A user will get all permissions granted to these groups.'),
        related_name='newuser_set',  
        related_query_name='newuser',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='newuser_set',  
        related_query_name='newuser',
    )

    def __str__(self):
        return self.email

    def get_email_field_name(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff

class UserProfile(models.Model):
    user = models.OneToOneField(NewUser, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=150, blank=True, null=True)
    country = models.CharField(max_length=150, blank=True, null=True)
    postal_code = models.IntegerField(blank=True, null=True)
    about_me = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images', blank=True, null=True)


    def __str__(self):
        return self.user.username
    
class Status(models.Model):
    status_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.status_name

@receiver(post_migrate)
def create_initial_status(sender, **kwargs):
    if sender.name == "cselect_app":  
        Status.objects.get_or_create(status_name='new')

class Product(models.Model):
    product_code = models.CharField(max_length=50, null=True)
    product_name = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)
    category = models.CharField(max_length=100, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    quantity = models.IntegerField(null=True)
    attachments = models.FileField(upload_to='attachments/', null=True, blank=True)

    def display_image(self):
        if self.attachments:
            return '<img src="%s" width="50" height="50" />' % self.attachments.url
        else:
            return 'No Image'

    display_image.allow_tags = True
    display_image.short_description = 'Image'

    def __str__(self):
        return self.product_name
    
class Cart(models.Model):
    user = models.OneToOneField(NewUser, on_delete=models.CASCADE)
    items = models.ManyToManyField(Product, through='CartItem')

    def __str__(self):
        return f"Cart - {self.user.username}"


class Order(models.Model):
    user = models.ForeignKey(NewUser, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def save(self, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=self.user)
        cart_items = CartItem.objects.filter(cart=cart)
        self.total_amount = sum(item.product.price * item.quantity for item in cart_items)
        super(Order, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"Order - {self.id} - {self.user}"

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.product.quantity -= self.quantity
            self.product.save()

        super(CartItem, self).save(*args, **kwargs)

    def __str__(self):
        return f"CartItem - {self.product.product_name} - Quantity: {self.quantity}"
    
class OrderDetail(models.Model):
    cart_item = models.ForeignKey(CartItem, on_delete=models.CASCADE, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)

    def __str__(self):
        return f"OrderDetail - {self.order.id} - {self.product.product_name}"
    