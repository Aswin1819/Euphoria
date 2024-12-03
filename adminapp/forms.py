from django import forms
from .models import Products,Variant,Images,Coupon,Offer
import re

class ProductForm(forms.ModelForm):
    # Define separate fields for each image
    image1 = forms.ImageField(required=False)
    image2 = forms.ImageField(required=False)
    image3 = forms.ImageField(required=False)
    image4 = forms.ImageField(required=False)

    class Meta:
        model = Products
        fields = ['name', 'description', 'brand', 'category', 'image1', 'image2', 'image3', 'image4']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'required': True}),
            'brand': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'category': forms.Select(attrs={'class': 'form-control', 'required': True}),
        }
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or not re.match(r'^[\w\s]+$', name):
            raise forms.ValidationError('Enter a valid name(alphabets)')
        return name
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if not description and not re.match(r'^[\w\s]+$', description):
            raise forms.ValidationError('Enter a proper description')
        return description
    
        

#modelform_factory is used in the view
class VariantForm(forms.ModelForm):
    class Meta:
        model = Variant
        fields = ['id','weight', 'price', 'stock']
        widgets = {
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Weight (in grams)', 'required': True,'min':0}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price', 'required': True,'min':0}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Stock', 'required': True}),
        }
    
    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight is not None and weight < 0:
            raise forms.ValidationError('Enter a Valid weight')
        if weight > 1000:
            raise forms.ValidationError('weight must be less than 1000g')
        return weight
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError("Price must be a positive number.")
        return price

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock < 0:  
            raise forms.ValidationError("Stock must be a non-negative number.")
        if stock > 1000:
            raise forms.ValidationError("Stock must be less than 1000")
        return stock
    
    
    
class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = [
            'code', 
            'discount_amount', 
            'discount_percentage', 
            'valid_from', 
            'valid_to', 
            'minimum_order_amount', 
            'max_discount_amount', 
            'max_usage_per_person', 
            
        ]
        widgets = {
            'code': forms.TextInput(attrs={'placeholder': 'Coupon Code', 'class': 'form-control', 'required': True}),
            'discount_amount': forms.NumberInput(attrs={'placeholder': 'Discount Amount', 'class': 'form-control'}),
            'discount_percentage': forms.NumberInput(attrs={'placeholder': 'Discount Percentage', 'class': 'form-control'}),
            'valid_from': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'valid_to': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'minimum_order_amount': forms.NumberInput(attrs={'placeholder': 'Minimum Order Amount', 'class': 'form-control'}),
            'max_discount_amount': forms.NumberInput(attrs={'placeholder': 'Max Discount Amount', 'class': 'form-control'}),
            'max_usage_per_person': forms.NumberInput(attrs={'placeholder': 'Max Usage Per Person', 'class': 'form-control'}),
          
        }
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code:
            raise forms.ValidationError("Code cant be empty")
        if not code.isalnum():
            raise forms.ValidationError("Enter a valid code")
        return code
    
    def clean_discount_amount(self):
        discount_amount = self.cleaned_data.get('discount_amount')
        if discount_amount:          
            if discount_amount < 0:
                raise forms.ValidationError("Enter a positive number")
        return discount_amount
    
    def clean_discount_percentage(self):
        discount_percentage = self.cleaned_data.get('discount_percentage')
        if discount_percentage:
            if discount_percentage < 0:
                raise forms.ValidationError('Enter a valid Perscentage')
        return discount_percentage
    
    def clean(self):
        cleaned_data = super().clean()
        valid_from = cleaned_data.get('valid_from')
        valid_to = cleaned_data.get('valid_to')
        discount_amount = cleaned_data.get('discount_amount')
        minimum_order_amount = cleaned_data.get('minimum_order_amount')
        discount_percentage = cleaned_data.get('discount_percentage')
        

        if valid_from and valid_to and valid_to <= valid_from:
            raise forms.ValidationError("Valid To must be later than Valid From.")
        if discount_amount > minimum_order_amount:
            raise forms.ValidationError("Discount amount must be less than minimum order")
        if not discount_percentage and not discount_amount:
            raise forms.ValidationError("You must specify either a discount percentage or a discount amount.")
        if discount_percentage and (discount_percentage <= 0 or discount_percentage > 100):
            raise forms.ValidationError("Discount percentage must be between 1 and 100.")
        
        return cleaned_data
    def clean_minimum_order_amount(self):
        minimum_order_amount = self.cleaned_data.get('minimum_order_amount')
        if minimum_order_amount < 0:
            raise forms.ValidationError("Minimun order amount cant be negative")
        return minimum_order_amount
    
    def clean_max_discount_amount(self):
        max_discount_amount = self.cleaned_data.get('max_discount_amount')
        if not max_discount_amount:
            raise forms.ValidationError("This field can't be empty")
        if max_discount_amount < 0:
            raise forms.ValidationError("This Field cant be negative")
        return max_discount_amount
    
    def clean_max_usage_per_person(self):
        max_usage_per_person = self.cleaned_data.get('max_usage_per_person')
        if not max_usage_per_person:
            raise forms.ValidationError("This field cant be empty")
        if max_usage_per_person <= 0 :
            raise forms.ValidationError("This field cant be less than 1")
        return max_usage_per_person
    
    



class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ['name', 'description', 'discount_percentage', 'discount_amount', 'start_date', 'end_date', 'products', 'categories']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Offer Name', 'class': 'form-control', 'required': True}),
            'description': forms.Textarea(attrs={'placeholder': 'Offer Description', 'class': 'form-control', 'rows': 3}),
            'discount_percentage': forms.NumberInput(attrs={'placeholder': 'Discount Percentage', 'class': 'form-control'}),
            'discount_amount': forms.NumberInput(attrs={'placeholder': 'Discount Amount', 'class': 'form-control'}),
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'products': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'categories': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
        
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Name can't be Empty")
        if not name.isalnum():
            raise forms.ValidationError("Enter a valid name")
        return name    
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if not description:
            raise forms.ValidationError("Description can't be Empty")
        if not re.match(r'^[\w\s]+$', description):
            raise forms.ValidationError("Enter a valid description")
        return description
    
    
    
    
    def clean(self):
        cleaned_data = super().clean()
        discount_percentage = cleaned_data.get('discount_percentage')
        discount_amount = cleaned_data.get('discount_amount')
        products = cleaned_data.get('products')
        categories = cleaned_data.get('categories')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # Ensure at least one type of discount is provided
        if not discount_percentage and not discount_amount:
            raise forms.ValidationError("You must specify either a discount percentage or a discount amount.")

        # Ensure discount values are within valid range
        if discount_percentage and (discount_percentage <= 0 or discount_percentage > 100):
            raise forms.ValidationError("Discount percentage must be between 1 and 100.")

        if discount_amount and discount_amount <= 0:
            raise forms.ValidationError("Discount amount must be greater than 0.")
        
        if not products.exists() and not categories.exists():
            raise forms.ValidationError("An offer must target at least one product or category.")

        if products.exists() and categories.exists():
            raise forms.ValidationError("An offer cannot target both products and categories simultaneously.")
        
        if start_date and end_date and end_date <= start_date:
            raise forms.ValidationError("End date must be greater than the start date")
        

        return cleaned_data

    