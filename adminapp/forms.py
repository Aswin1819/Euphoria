from django import forms
from .models import Products, Variant,Images
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
    
    def clean_image1(self):
        return self.clean_image('image1')

    def clean_image2(self):
        return self.clean_image('image2')

    def clean_image3(self):
        return self.clean_image('image3')

    def clean_image4(self):
        return self.clean_image('image4')

    def clean_image(self, image_field):
        image = self.cleaned_data.get(image_field)
        if image:
            valid_extensions = ['jpg', 'jpeg', 'png']
            file_extension = image.name.split('.')[-1].lower()

            if file_extension not in valid_extensions:
                raise forms.ValidationError("Image must be in JPG, JPEG, or PNG format.")
            
            
            max_size = 5 * 1024 * 1024
            if image.size > max_size:
                raise forms.ValidationError("Image size must not exceed 5MB.")

        return image
        
    
    
    
    

    
        

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
        return stock
    