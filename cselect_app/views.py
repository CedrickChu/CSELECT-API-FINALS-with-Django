from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm, CheckoutForm, CustomUserCreationForm, UserAndProfileForm, UserProfileForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.views import View
from .models import CartItem, Order, Status, OrderDetail, Product, Cart, NewUser
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from django.contrib.auth.views import LogoutView
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView


from django.http import Http404
from .serializers import (
    NewUserSerializer,
    OrderSerializer,
    CartItemSerializer,
    ProductSerializer,
    StatusSerializer,
    CartItemCreateUpdateSerializer,
)
from rest_framework.generics import RetrieveAPIView




def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend='django.contrib.auth.custom_auth_backend.CustomAuthBackend')
            print(redirect('dashboard'))
            return redirect('dashboard')  
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

class CustomLogoutView(LogoutView):
    def post(self, request, *args, **kwargs):
        self.next_page = '/' 
        if self.logout(request):
            if self.next_page:
                return redirect(self.next_page)
        return super().post(request, *args, **kwargs)

@login_required
def home_view(request):
    product_items = Product.objects.all()
    cart, created = Cart.objects.get_or_create(user=request.user)

    if created:
        cart.save()

    cart_items = CartItem.objects.filter(cart=cart)

    total_cart_price = sum(item.product.price * item.quantity for item in cart_items)
    cart.total = total_cart_price 
    cart.save() 

    return render(request, 'dashboard.html', {'product_items': product_items, 'cart_items': cart_items, 'cart': cart})

def register_view(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            # Log the user in
            login(request, user, backend='django.contrib.auth.custom_auth_backend.CustomAuthBackend')
            messages.success(request, 'Registration successful. You are now logged in.')
            return redirect('dashboard')
    else:
        user_form = CustomUserCreationForm()
        profile_form = UserProfileForm()

    return render(request, 'register.html', {'user_form': user_form, 'profile_form': profile_form})

class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = CustomAuthenticationForm
    

@method_decorator(login_required, name='dispatch')
class CheckoutView(LoginRequiredMixin, View):
    template_name = 'checkout.html'
    thank_you_template_name = 'order_complete.html'

    def get(self, request, *args, **kwargs):
        # Retrieve the user's cart
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Retrieve cart items for the user's cart
        cart_items = CartItem.objects.filter(cart=cart)

        if cart_items.exists():
            total_amount = sum(item.product.price * item.quantity for item in cart_items)
            form = CheckoutForm()
            return render(request, self.template_name, {
                'cart_items': cart_items,
                'total_amount': total_amount,
                'form': form
            })
        else:
            return render(request, self.template_name, {
                'cart_items': [],
                'total_amount': 0,
                'form': CheckoutForm()
            })

    def post(self, request, *args, **kwargs):
        status_new = Status.objects.get(status_name='new')

        cart, created = Cart.objects.get_or_create(user=request.user)

        # Retrieve cart items for the user's cart
        cart_items = CartItem.objects.filter(cart=cart)

        if cart_items.exists():
            
            order = Order.objects.create(user=request.user, status=status_new)

            for cart_item in cart_items:
                OrderDetail.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.product.price,
                    status=status_new
                )

            # Clear the cart
            cart_items.delete()

            return render(request, self.thank_you_template_name)
        else:
            return redirect('dashboard')

    
def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'product_detail.html', {'product': product})

def upload_attachment(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=product_id)

        attachment_file = request.FILES.get('attachment')

        if attachment_file:
            product.attachments = attachment_file
            product.save()

    return render(request, 'upload_attachment.html')

@login_required
def add_to_cart(request, item_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=item_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        cart_item.quantity += 1
        cart_item.save()

        return JsonResponse({'status': 'success', 'message': 'Item added to cart'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
        

def remove_from_cart(request, item_id):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, id=item_id)
    cart_item.delete()
    return redirect('cart')

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)

    if created:
        cart.save()

    cart_items = CartItem.objects.filter(cart=cart)

    total_cart_price = sum(item.product.price * item.quantity for item in cart_items)
    cart.total = total_cart_price 
    cart.save() 

    return render(request, 'cart.html', {'cart_items': cart_items, 'cart': cart})

def get_cart_data(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
    else:
        cart_items = []

    cart_data = [{'name': item.product.product_name, 'price': item.product.price, 'quantity': item.quantity} for item in cart_items]
    return JsonResponse(cart_data, safe=False)

class NewUserViewSet(viewsets.ModelViewSet):
    queryset = NewUser.objects.all()
    serializer_class = NewUserSerializer

class StatusViewSet(viewsets.ModelViewSet):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CartItemCreateUpdateSerializer
        return CartItemSerializer

@login_required
def update_profile(request):
    user_profile = request.user.userprofile

    if request.method == 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # AJAX form submission
            form = UserAndProfileForm(request.POST, request.FILES, instance=user_profile)
            if form.is_valid():
                form.save()
                return JsonResponse({"success": True, "message": "Profile updated successfully"})
            else:
                return JsonResponse({"success": False, "message": "Error updating profile", "errors": form.errors})
        else:
            # Regular form submission
            form = UserAndProfileForm(request.POST, request.FILES, instance=user_profile)
            if form.is_valid():
                form.save()
                return JsonResponse({"success": True, "message": "Profile updated successfully"})
            else:
                # Form is not valid, render the template with the form and errors
                return render(request, 'profile.html', {'form': form})

    form = UserAndProfileForm(instance=user_profile)
    return render(request, 'profile.html', {'form': form})