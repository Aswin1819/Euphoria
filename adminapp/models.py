from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from datetime import timedelta

class EuphoUserManager(BaseUserManager):
    def create_user(self, email, username, phone, password=None, **extra_fields):
        if not email:
            raise ValueError("User must have an email address")
        if not username:
            raise ValueError("User must have a Username")
        
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active',True)
        user = self.model(
            email=email,
            username=username,
            phone=phone,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, username, phone, password, **extra_fields)

class EuphoUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone']

    objects = EuphoUserManager()

    def __str__(self):
        return self.email

class OTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    username = models.CharField(max_length=150, null=True)
    password = models.CharField(max_length=128, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        self.expires_at = timezone.now() + timedelta(seconds=60)
        super().save(*args, **kwargs)

    def is_valid(self):
        return timezone.now() <= self.expires_at

    def __str__(self):
        return f"OTP for {self.email}"
    
    
    
class BaseModel(models.Model):
    added_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Brand(BaseModel):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    

    
class Category(BaseModel):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name
    
    
class Images(models.Model):
    images = models.ImageField(upload_to="product_Images/")
    alt_text = models.CharField( max_length=255,blank=True)
    product = models.ForeignKey('Products',on_delete=models.CASCADE,related_name='product_images', null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Images {self.id}"
    
    @property
    def url(self):
        return self.images.url
    
    def delete(self,*args,**kwargs):
        self.is_deleted=True
        self.save()
            

class Products(models.Model):
    name = models.CharField( max_length=255)
    description = models.TextField()
    # price = models.DecimalField(max_digits=10, decimal_places=2)
    # stock = models.PositiveIntegerField()
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    # weight = models.IntegerField(null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    
    def __str__(self):
        return self.name
        
        
class Variant(models.Model):
    product = models.ForeignKey(Products, related_name='variants', on_delete=models.CASCADE)
    weight = models.PositiveIntegerField()  # In grams (g)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price for this specific variant
    stock = models.PositiveIntegerField()  # Stock specific to this variant
    
    class Meta:
        unique_together = ('product', 'weight')  # Ensure uniqueness for weight per product

    def __str__(self):
        return f"{self.product.name} - {self.weight}g"
