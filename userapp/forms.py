from django import forms
import re
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm,PasswordChangeForm
from adminapp.models import Address,Review

# from adminapp.models import EuphoUser

class UserLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email',
        'required': True,
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your password',
        'required': True,
    }))
    
    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        UserModel = get_user_model()
        user = None  # Initialize user variable

        if email and password:
            try:
                user = UserModel.objects.get(email=email)
            except UserModel.DoesNotExist:
                raise forms.ValidationError('Invalid email or password.')

            if not user.check_password(password):
                raise forms.ValidationError('Invalid password.')

        # Save user instance in cleaned_data for later use
        self.cleaned_data['user'] = user  
        return self.cleaned_data



EuphoUser = get_user_model()

class UserSignupForm(UserCreationForm):
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'required': True,
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'required': True,
        })
    )

    class Meta:
        model = EuphoUser
        fields = ['username', 'email', 'phone']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your username',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email',
                'required': True,
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number',
                'required': True,
            }),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username.isalpha():
            raise forms.ValidationError('Username can only contain alphabetic characters')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if EuphoUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Email is already registered')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit():
            raise forms.ValidationError('Phone number must contain only digits')
        if len(phone) != 10:
            raise forms.ValidationError('Phone number must be exactly 10 digits')
        return phone
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 6:
            raise forms.ValidationError('Password must be at least 6 characters long')
        return password1
    
    
    

class ChangeProfileForm(forms.ModelForm):
    class Meta:
        model = EuphoUser
        fields = ['username','gender','email','phone','profile_image']
        
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username.isalpha():
            raise forms.ValidationError('Username must be alphabets')
        return username   
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit():
            raise forms.ValidationError('Phone number must contain only digits')
        if len(phone) != 10:
            raise forms.ValidationError('Phone number must be exactly 10 digits')
        return phone            
        
        
class ChangePasswordForm(PasswordChangeForm):
    class Meta:
        model = EuphoUser
        fields = ['old_password','new_password1','new_password2']
        

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_type', 'address', 'city', 'place', 'landmark', 'pincode', 'phone']
        widgets = {
            'address_type': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'place': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Place'}),
            'landmark': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Landmark (optional)'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pincode'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
        }



class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review_text']