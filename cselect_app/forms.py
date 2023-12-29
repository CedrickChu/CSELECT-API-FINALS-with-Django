from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm

from .models import NewUser, Order, CartItem, UserProfile

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = NewUser
        fields = ['email', 'username', 'phone', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['phone'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        
class CustomAuthenticationForm(AuthenticationForm):
    pass

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        

class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['quantity'] 
    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity < 1:
            raise forms.ValidationError("Quantity should be at least 1.")
        return quantity
    
class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})
        
        
class UserAndProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    address = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=100, required=False)
    country = forms.CharField(max_length=100, required=False)
    postal_code = forms.CharField(max_length=20, required=False)
    about_me = forms.CharField(widget=forms.Textarea, required=False)
    profile_image = forms.ImageField(required=False)

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'address', 'city', 'country', 'postal_code', 'about_me', 'profile_image']

    def __init__(self, *args, **kwargs):
        super(UserAndProfileForm, self).__init__(*args, **kwargs)

        if 'instance' in kwargs:
            user_instance = kwargs['instance'].user
            self.fields['username'].initial = user_instance.username
            self.fields['email'].initial = user_instance.email

    def save(self, commit=True):
        user_instance = self.instance.user if self.instance else NewUser()
        user_instance.username = self.cleaned_data['username']
        user_instance.email = self.cleaned_data['email']
        if commit:
            user_instance.save()

        profile_instance = super(UserAndProfileForm, self).save(commit=False)
        profile_instance.user = user_instance
        if commit:
            profile_instance.save()

        return profile_instance
    
    
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'profile_image']