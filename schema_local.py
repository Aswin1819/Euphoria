# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AccountEmailaddress(models.Model):
    email = models.CharField(unique=True, max_length=254)
    verified = models.BooleanField()
    primary = models.BooleanField()
    user = models.ForeignKey('AdminappEuphouser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'account_emailaddress'
        unique_together = (('user', 'email'), ('user', 'primary'),)


class AccountEmailconfirmation(models.Model):
    created = models.DateTimeField()
    sent = models.DateTimeField(blank=True, null=True)
    key = models.CharField(unique=True, max_length=64)
    email_address = models.ForeignKey(AccountEmailaddress, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'account_emailconfirmation'


class AdminappAddress(models.Model):
    id = models.BigAutoField(primary_key=True)
    address_type = models.CharField(max_length=10)
    address = models.TextField()
    city = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    landmark = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    user = models.ForeignKey('AdminappEuphouser', models.DO_NOTHING)
    is_primary = models.BooleanField()
    is_deleted = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'adminapp_address'


class AdminappBrand(models.Model):
    id = models.BigAutoField(primary_key=True)
    added_date = models.DateTimeField()
    updated_date = models.DateTimeField()
    is_active = models.BooleanField()
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'adminapp_brand'


class AdminappCart(models.Model):
    id = models.BigAutoField(primary_key=True)
    session_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    user = models.ForeignKey('AdminappEuphouser', models.DO_NOTHING, blank=True, null=True)
    coupon = models.ForeignKey('AdminappCoupon', models.DO_NOTHING, blank=True, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'adminapp_cart'


class AdminappCartitem(models.Model):
    id = models.BigAutoField(primary_key=True)
    quantity = models.IntegerField()
    cart = models.ForeignKey(AdminappCart, models.DO_NOTHING)
    product = models.ForeignKey('AdminappProducts', models.DO_NOTHING)
    variant = models.ForeignKey('AdminappVariant', models.DO_NOTHING)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'adminapp_cartitem'


class AdminappCategory(models.Model):
    id = models.BigAutoField(primary_key=True)
    added_date = models.DateTimeField()
    updated_date = models.DateTimeField()
    is_active = models.BooleanField()
    name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'adminapp_category'


class AdminappCoupon(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.CharField(unique=True, max_length=20)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    max_usage_per_person = models.IntegerField()
    active = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'adminapp_coupon'


class AdminappEuphouser(models.Model):
    id = models.BigAutoField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    username = models.CharField(max_length=100)
    email = models.CharField(unique=True, max_length=254)
    phone = models.CharField(max_length=15)
    is_active = models.BooleanField()
    is_staff = models.BooleanField()
    is_superuser = models.BooleanField()
    date_joined = models.DateTimeField()
    gender = models.CharField(max_length=6)
    profile_image = models.CharField(max_length=100, blank=True, null=True)
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'adminapp_euphouser'


class AdminappEuphouserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    euphouser = models.ForeignKey(AdminappEuphouser, models.DO_NOTHING)
    group = models.ForeignKey('AuthGroup', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'adminapp_euphouser_groups'
        unique_together = (('euphouser', 'group'),)


class AdminappEuphouserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    euphouser = models.ForeignKey(AdminappEuphouser, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'adminapp_euphouser_user_permissions'
        unique_together = (('euphouser', 'permission'),)


class AdminappImages(models.Model):
    id = models.BigAutoField(primary_key=True)
    images = models.CharField(max_length=100)
    alt_text = models.CharField(max_length=255)
    is_deleted = models.BooleanField()
    product = models.ForeignKey('AdminappProducts', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'adminapp_images'


class AdminappOffer(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    last_updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'adminapp_offer'


class AdminappOfferCategories(models.Model):
    id = models.BigAutoField(primary_key=True)
    offer = models.ForeignKey(AdminappOffer, models.DO_NOTHING)
    category = models.ForeignKey(AdminappCategory, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'adminapp_offer_categories'
        unique_together = (('offer', 'category'),)


class AdminappOfferProducts(models.Model):
    id = models.BigAutoField(primary_key=True)
    offer = models.ForeignKey(AdminappOffer, models.DO_NOTHING)
    products = models.ForeignKey('AdminappProducts', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'adminapp_offer_products'
        unique_together = (('offer', 'products'),)


class AdminappOrder(models.Model):
    id = models.BigAutoField(primary_key=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField()
    user = models.ForeignKey(AdminappEuphouser, models.DO_NOTHING)
    paymentmethod = models.ForeignKey('AdminappPaymentmethod', models.DO_NOTHING, blank=True, null=True)
    address = models.ForeignKey(AdminappAddress, models.DO_NOTHING, blank=True, null=True)
    is_paid = models.BooleanField()
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    coupon = models.ForeignKey(AdminappCoupon, models.DO_NOTHING, blank=True, null=True)
    total_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'adminapp_order'


class AdminappOrderitem(models.Model):
    id = models.BigAutoField(primary_key=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    order = models.ForeignKey(AdminappOrder, models.DO_NOTHING)
    product = models.ForeignKey('AdminappProducts', models.DO_NOTHING)
    cancellation_reason = models.TextField(blank=True, null=True)
    last_updated = models.DateTimeField()
    return_reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'adminapp_orderitem'


class AdminappOtp(models.Model):
    id = models.BigAutoField(primary_key=True)
    email = models.CharField(max_length=254)
    otp = models.CharField(max_length=6)
    username = models.CharField(max_length=150, blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True)
    created_at = models.DateTimeField()
    expires_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'adminapp_otp'


class AdminappPaymentmethod(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'adminapp_paymentmethod'


class AdminappProducts(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    brand = models.ForeignKey(AdminappBrand, models.DO_NOTHING)
    is_active = models.BooleanField()
    is_featured = models.BooleanField()
    category = models.ForeignKey(AdminappCategory, models.DO_NOTHING)
    popularity = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'adminapp_products'


class AdminappReview(models.Model):
    id = models.BigAutoField(primary_key=True)
    rating = models.SmallIntegerField()
    review_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()
    product = models.ForeignKey(AdminappProducts, models.DO_NOTHING)
    user = models.ForeignKey(AdminappEuphouser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'adminapp_review'
        unique_together = (('product', 'user'),)


class AdminappTransaction(models.Model):
    id = models.BigAutoField(primary_key=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10)
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField()
    product = models.ForeignKey(AdminappProducts, models.DO_NOTHING, blank=True, null=True)
    wallet = models.ForeignKey('AdminappWallet', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'adminapp_transaction'


class AdminappUsercoupon(models.Model):
    id = models.BigAutoField(primary_key=True)
    used_at = models.DateTimeField()
    coupon = models.ForeignKey(AdminappCoupon, models.DO_NOTHING)
    user = models.ForeignKey(AdminappEuphouser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'adminapp_usercoupon'


class AdminappVariant(models.Model):
    id = models.BigAutoField(primary_key=True)
    weight = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    product = models.ForeignKey(AdminappProducts, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'adminapp_variant'
        unique_together = (('product', 'weight'),)


class AdminappWallet(models.Model):
    id = models.BigAutoField(primary_key=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.OneToOneField(AdminappEuphouser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'adminapp_wallet'


class AdminappWishlist(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    user = models.ForeignKey(AdminappEuphouser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'adminapp_wishlist'


class AdminappWishlistitem(models.Model):
    id = models.BigAutoField(primary_key=True)
    added_at = models.DateTimeField()
    product = models.ForeignKey(AdminappProducts, models.DO_NOTHING)
    variant = models.ForeignKey(AdminappVariant, models.DO_NOTHING)
    wishlist = models.ForeignKey(AdminappWishlist, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'adminapp_wishlistitem'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AdminappEuphouser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class DjangoSite(models.Model):
    domain = models.CharField(unique=True, max_length=100)
    name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'django_site'


class SocialaccountSocialaccount(models.Model):
    provider = models.CharField(max_length=200)
    uid = models.CharField(max_length=191)
    last_login = models.DateTimeField()
    date_joined = models.DateTimeField()
    extra_data = models.JSONField()
    user = models.ForeignKey(AdminappEuphouser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialaccount'
        unique_together = (('provider', 'uid'),)


class SocialaccountSocialapp(models.Model):
    provider = models.CharField(max_length=30)
    name = models.CharField(max_length=40)
    client_id = models.CharField(max_length=191)
    secret = models.CharField(max_length=191)
    key = models.CharField(max_length=191)
    provider_id = models.CharField(max_length=200)
    settings = models.JSONField()

    class Meta:
        managed = False
        db_table = 'socialaccount_socialapp'


class SocialaccountSocialappSites(models.Model):
    id = models.BigAutoField(primary_key=True)
    socialapp = models.ForeignKey(SocialaccountSocialapp, models.DO_NOTHING)
    site = models.ForeignKey(DjangoSite, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialapp_sites'
        unique_together = (('socialapp', 'site'),)


class SocialaccountSocialtoken(models.Model):
    token = models.TextField()
    token_secret = models.TextField()
    expires_at = models.DateTimeField(blank=True, null=True)
    account = models.ForeignKey(SocialaccountSocialaccount, models.DO_NOTHING)
    app = models.ForeignKey(SocialaccountSocialapp, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialtoken'
        unique_together = (('app', 'account'),)
