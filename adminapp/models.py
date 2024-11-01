from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

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
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('others', 'Others'),
    ]
    
    
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, default='male')  # Default value
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
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
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    popularity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    
    
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


class Address(models.Model):
    ADDRESS_TYPES = [
        ('home', 'Home'),
        ('work', 'Work'),
    ]

    user = models.ForeignKey(EuphoUser, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES, default='home')
    address = models.TextField()
    city = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    landmark = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    is_primary = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        # Check if there is already a primary address for the user
        if not Address.objects.filter(user=self.user, is_primary=True).exists():
            self.is_primary = True  # Make this the primary address if no other exists
        super(Address, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.username} - {self.address_type.capitalize()} Address'
    
    
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    session_id = models.CharField(max_length=255, blank=True, null=True)  # For guests
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart - User: {self.user or 'Guest'}"
    
    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.quantity} of {self.product.name} - {self.variant.weight}g"
    
    def get_total_price(self):
        return self.variant.price * self.quantity
    
    
    
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[
        ("Pending", "Pending"), 
        ("delivered", "delivered"),
        ("Cancelled","Cancelled"),
        ("Returned","Returned"),
        ("Refunded","Refunded"),
        ("Failed","Failed")])

    payment_method = models.CharField(max_length=50,default="Cash on Delivery")
    cancellation_reason = models.TextField(null=True,blank=True)
    return_reason = models.TextField(null=True,blank=True)
    
    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total_price(self):
        return self.price * self.quantity