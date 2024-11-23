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
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone']

    objects = EuphoUserManager()

    def __str__(self):
        return self.email
    
    def get_primary_address(self):
        return self.addresses.filter(is_primary=True).first()

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
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return self.name
    
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / reviews.count()
        return 0
        
        
class Variant(models.Model):
    product = models.ForeignKey(Products, related_name='variants', on_delete=models.CASCADE)
    weight = models.PositiveIntegerField()  # In grams (g)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price for this specific variant
    stock = models.PositiveIntegerField()  # Stock specific to this variant
    
    class Meta:
        unique_together = ('product', 'weight')  # Ensure uniqueness for weight per product

    def __str__(self):
        return f"{self.product.name} - {self.weight}g"


class Review(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    review_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')





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
    is_deleted = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
       
        if not Address.objects.filter(user=self.user, is_primary=True).exists():
            self.is_primary = True  
        super(Address, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.address},{self.city}'
    
    
    
class Coupon(models.Model):
    code = models.CharField(max_length=20,unique=True)
    discount_amount = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    discount_percentage = models.DecimalField(max_digits=5,decimal_places=2,null=True,blank=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    minimum_order_amount = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    max_discount_amount = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    max_usage_per_person = models.PositiveIntegerField(default=1)
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.code
    
    def is_valid(self):
        now = timezone.now()
        return self.active and self.valid_from <= now <= self.valid_to
    

class UserCoupon(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon,on_delete=models.Case)
    used_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user} used {self.coupon.code}"    

     
    
    
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    session_id = models.CharField(max_length=255, blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    discount = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    coupon = models.ForeignKey(Coupon,on_delete=models.SET_NULL,null=True,blank=True)

    def __str__(self):
        return f"Cart - User: {self.user or 'Guest'}"
    
    # def get_discount_price(self):
    #     total = sum(item.get_total_price() for item in self.items.all())
    #     return total - self.discount
    
    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())
    
    def get_discount_price(self):
        # Total price after applying the discount
        return self.get_total_price() - self.discount
    
    def get_original_price(self):
        # Total price without any discounts
        return sum(item.variant.price * item.quantity for item in self.items.all())
    
    def get_savings(self):
        # Total savings (original price - discounted price + additional discount)
        return self.get_original_price() - self.get_total_price() + self.discount
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    def __str__(self):
        return f"{self.quantity} of {self.product.name} - {self.variant.weight}g"
    
    def get_total_price(self):
        return (self.price or self.variant.price) * self.quantity
    

class PaymentMethod(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name
    
    


    



class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    paymentmethod = models.ForeignKey(PaymentMethod,on_delete=models.SET_NULL,null=True,default=1)
    address = models.ForeignKey(Address,on_delete=models.PROTECT,null=True,blank=True)
    
    #razorpay_fieldss
    razorpay_payment_id = models.CharField(max_length=100,blank=True,null=True)
    is_paid = models.BooleanField(default=False)
    
    
    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[
        ("Pending", "Pending"), 
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
        ("Returned", "Returned"),
        ("Refunded", "Refunded"),
        ("Failed", "Failed"),
        ('Shipped','Shipped'),
        ('Out of Delivery','Out of Delivery'),
    ], default="Shipped")
    cancellation_reason = models.TextField(null=True,blank=True)
    return_reason = models.TextField(null=True,blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def get_total_price(self):
        return self.price * self.quantity
    
    

class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='wishlists')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Wishlist of {self.user.username}"
    


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist,on_delete=models.CASCADE,related_name='items')
    product = models.ForeignKey(Products,on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant,on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.variant.weight}"
    

class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def credit(self, amount):
        """Increase the wallet balance."""
        self.balance += amount
        self.save()

    def debit(self, amount):
        """Decrease the wallet balance, if sufficient funds exist."""
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False
    

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]
    
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)
    product = models.ForeignKey(Products, on_delete=models.SET_NULL, null=True, blank=True, related_name="transactions")

    def __str__(self):
        return f"{self.transaction_type.capitalize()} of ₹{self.amount} on {self.timestamp.strftime('%Y-%m-%d')}"

class Offer(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True,null=True)
    discount_percentage = models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True)
    discount_amount = models.DecimalField(max_digits=5,decimal_places=2,null=True,blank=True)
    products = models.ManyToManyField(Products,related_name='offers',blank=True)
    categories = models.ManyToManyField(Category,related_name='offers',blank=True)
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

    
    