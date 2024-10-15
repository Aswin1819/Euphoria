from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

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
                'placeholder': 'Enter your full name',
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

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if EuphoUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Email is already registered')
        return email
    