from django import forms
from .models import Products, Variant,Images

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

    # Optional: You can add custom validation to check the number of images if required
    # def clean(self):
    #     cleaned_data = super().clean()
    #     images = [cleaned_data.get('image1'), cleaned_data.get('image2'),
    #               cleaned_data.get('image3'), cleaned_data.get('image4')]
    #     # Optionally check the number of images
    #     if not any(images):
    #         raise forms.ValidationError("At least one image is required.")
        


class VariantForm(forms.ModelForm):
    class Meta:
        model = Variant
        fields = ['weight', 'price', 'stock']
        widgets = {
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Weight (in grams)', 'required': True}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price', 'required': True}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Stock', 'required': True}),
        }
