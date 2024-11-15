from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.hashers import make_password
from adminapp.models import EuphoUser,OTP,Products,Variant,Address,Cart,CartItem,Order,OrderItem,Category,PaymentMethod,Wishlist,WishlistItem,Coupon,UserCoupon
from decimal import Decimal
from django.contrib import messages
from userapp.userotp import generateAndSendOtp
from django.conf import settings
from .signals import userOtpVerified
from .forms import UserLoginForm,UserSignupForm,ChangeProfileForm,ChangePasswordForm,AddressForm,ReviewForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q,Min,Avg
from django.views.decorators.cache import never_cache
import razorpay

# Create your views here.


@never_cache
def userlogin(request):
    if request.user.is_authenticated:
        return redirect('userhome')

    if request.method == 'POST':
        form = UserLoginForm(request.POST or None)
        if form.is_valid():
            user = form.cleaned_data.get('user')  
            if user:
                if user.is_active: 
                    login(request, user,backend='django.contrib.auth.backends.ModelBackend')
                    print(user.username)
                    return redirect('userhome')
                else:
                    messages.warning(request,"Your account is not active.")
        else:
            print(form.errors)  
            messages.warning(request, "Invalid email or password.")
    else:
        form = UserLoginForm()

    return render(request, 'userlogin.html', {'form': form})

@never_cache
def usersignup(request):
    if request.user.is_authenticated:
        return redirect('userhome')
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.is_active = False #deactivate user untill otp verification
            new_user.save()
            
            otp = generateAndSendOtp(new_user.email)
            OTP.objects.create(email=new_user.email,otp=otp)
            
            messages.success(request, 'OTP sent to your email. Please validate.')
            return render(request, 'otp_validation.html', {'email': new_user.email})
        else:
            messages.warning(request,"Please correct the errors below")
    else:
        form = UserSignupForm()
    
    return render(request, 'usersignup.html',{'form':form})




@never_cache
def otpValidation(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp1 = request.POST.get('otp1')
        otp2 = request.POST.get('otp2')
        otp3 = request.POST.get('otp3')
        otp4 = request.POST.get('otp4')
        otp = otp1+otp2+otp3+otp4
        
        try:
            otpRecord = OTP.objects.get(email = email,otp = otp)
            if otpRecord.is_valid():
                userOtpVerified.send(sender = OTP, email = email)
                
                otpAll = OTP.objects.all()
                otpAll.delete()
                messages.success(request,"Account created successfully.Please Login!")
                return redirect('userlogin')
            else:
                messages.warning(request,"Otp has expired")    
        except OTP.DoesNotExist:
            messages.warning(request,"Invalid Otp")
                
    
        return render(request,'otp_validation.html',{'email':email})


@never_cache
def resendotp(request):
    if request.method =='POST':
        email = request.POST.get('email')
        
        otp = generateAndSendOtp(email)
        OTP.objects.create(email=email,otp=otp)
        
        messages.success(request,"A new OTP has send to your email")
        return render(request,'otp_validation.html',{'email':email})
    return render(request,'otp_validation.html')

@never_cache
def resendOtpForPass(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        otp = generateAndSendOtp(email)
        OTP.objects.create(email=email,otp=otp)
        
        messages.success(request,'A new OTP send to your email')
        return render(request,'forg_pass_otp.html',{'email':email})
    return render(request,'forg_pass_otp.html')


@never_cache
def forgPassEmailVerification(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            if EuphoUser.objects.filter(email=email).exists():
                otp = generateAndSendOtp(email)
                OTP.objects.create(email=email,otp=otp)
                return render(request,'forg_pass_otp.html',{'email':email})
            else:
                messages.warning(request,'email not exist')
        except:
            messages.warning(request,"Enter your email")
            return render(request,'forg_pass_email.html')        
        
    return render(request,'forg_pass_email.html')


@never_cache
def otpValidationForPass(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp1 = request.POST.get('otp1')
        otp2 = request.POST.get('otp2')
        otp3 = request.POST.get('otp3')
        otp4 = request.POST.get('otp4')
        otp = otp1 + otp2 + otp3 + otp4

        # Ensure all OTP parts are present
        if not all([otp1, otp2, otp3, otp4]):
            messages.warning(request, "OTP is incomplete")
            return render(request, 'forg_pass_otp.html', {'email': email})

        try:
            otpRecord = OTP.objects.get(email=email,otp=otp)
         
            if otpRecord.is_valid(): 
                userOtpVerified.send(sender=OTP, email=email)
                OTP.objects.filter(email=email).delete()
                
                messages.success(request, "OTP verified. Create New Password")
                return render(request, 'change_password.html', {'email': email})
            else:
                messages.warning(request, "OTP has expired")
        except OTP.DoesNotExist:
            messages.warning(request, "Invalid OTP")

        return render(request, 'forg_pass_otp.html', {'email': email})

    return render(request, 'forg_pass_otp.html')


@never_cache
def changePassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmPassword = request.POST.get('confirm_password')
        
       
        
        if password and confirmPassword and password==confirmPassword and len(password)>6:
            try:
                user = EuphoUser.objects.get(email=email)
                user.set_password(password)
                user.save()
                messages.success(request,'Password Succeessfully changed!!')
                return redirect('userlogin')
            except EuphoUser.DoesNotExist:
                messages.warning(request,"User does not exist")
        else:
            messages.warning(request,"Password not match or are empty or must be atleast 6 characters")
            return render(request,'change_password.html',{'email':email})
    
    return render(request,'change_password.html')


def userhome(request):
    # categories = Category.objects.filter(is_active=True)
    products = Products.objects.filter(category__is_active=True,brand__is_active=True).prefetch_related('variants').order_by('-popularity')
    latest_product = Products.objects.filter(category__is_active=True,brand__is_active=True).order_by('-created_at')[:4]
    featured = Products.objects.filter(is_featured=True,category__is_active=True,brand__is_active=True)
    return render(request,'user_home.html',{
        'products':products,
        'latest_products':latest_product,
        'featured_products':featured})


def shopNow(request):
    sort_option = request.GET.get('sort', 'popularity')
    search_query = request.GET.get('query','').strip()
    products = Products.objects.filter(
        category__is_active=True,
        brand__is_active=True,
    ).annotate(
        min_variant_price=Min('variants__price'),
        average_rating=Avg('reviews__rating')
    )
    # .prefetch_related('variants')
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)|Q(brand__name__icontains=search_query)
        )
    
    # Sort options
    if sort_option == 'price_low_to_high':
        products = products.order_by('min_variant_price')
    elif sort_option == 'price_high_to_low':
        products = products.order_by('-min_variant_price')
    elif sort_option == 'average_rating':
        products = products.order_by('average_rating')
    elif sort_option == 'featured':
        products = products.filter(is_featured=True)
    elif sort_option == 'new_arrivals':
        products = products.order_by('-created_at')
    elif sort_option == 'a_to_z':
        products = products.order_by('name')
    elif sort_option == 'z_to_a':
        products = products.order_by('-name')
    else:
        products = products.order_by('-popularity')

    # Pagination
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    is_ajax_request = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    print("Is AJAX request:", is_ajax_request)
    
    if is_ajax_request:
        html = render_to_string('partials/product_list.html', {'page_obj': page_obj})
        return JsonResponse({'html': html})


    return render(request, 'shopnow.html', {
        'page_obj': page_obj,
        'sort_option': sort_option,
        'search_query':search_query,
    })


def categoryProducts(request,category_id):
    try:        
        category = get_object_or_404(Category,id=category_id,is_active=True)
    except:
        return redirect(shopNow)
    
    products = Products.objects.filter(category=category,is_active=True)
    return render(request,'categoryproductsview.html',{
        'category':category,
        'products':products})



def productView(request, id):
    product = get_object_or_404(Products, id=id)
    product.popularity += 1
    product.save()
    
    average_rating = int(product.average_rating())
    variants = Variant.objects.filter(product=product)
    default_variant = variants.first() if variants else None

    related_products = Products.objects.filter(
        brand=product.brand,
        category__is_active=True,
        brand__is_active=True
    ).exclude(id=product.id)

    if request.user.is_authenticated:
        has_purchased = OrderItem.objects.filter(
            order__user=request.user, product=product, status='Delivered'
        ).exists()
        has_reviewed = product.reviews.filter(user=request.user).exists()
    else:
        has_purchased = False
        has_reviewed = False
        
    form=None
    if request.method == 'POST' and has_purchased and not has_reviewed:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('productView', id=id)  
    elif has_purchased and not has_reviewed:
        form = ReviewForm()

    # Retrieve existing reviews for the product
    reviews = product.reviews.all()

    return render(request, 'productview.html', {
        'product': product,
        'related_products': related_products,
        'variants': variants,
        'default_variant': default_variant,
        'reviews': reviews,
        'form': form,
        'has_purchased': has_purchased,
        'has_reviewed': has_reviewed,
        'average_rating':average_rating
    })


       

@never_cache
@login_required(login_url='userlogin')
def userProfileInformation(request):
    user = request.user

    profile_form = ChangeProfileForm(instance=user)
    
    password_form = ChangePasswordForm(user=user)

    if request.method == 'POST':
       
        if 'profile_submit' in request.POST:
            profile_form = ChangeProfileForm(request.POST, request.FILES, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                print("profile edited successfully")
                messages.success(request,'profile edited successfully')
                return redirect('userProfileInformation')
            else:
                print(profile_form.errors)

        elif 'password_submit' in request.POST:
            password_form = ChangePasswordForm(user=user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)  # Keeps the user logged in
                print("Password changed successfully")
                messages.success(request,'Password changed successfully')
                return redirect('userProfileInformation')
            else:
                print(password_form.errors)

    return render(request, 'userprofileinformation.html', {
        'profile_form': profile_form,
        'password_form': password_form,
    })
    
        
@never_cache
@login_required(login_url='userlogin')
def userManageAddress(request):
    
    user_address = Address.objects.filter(user=request.user,is_deleted=False)
    
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user=request.user
            address.save()
            messages.success(request,"Address added successfully")
            return redirect(userManageAddress)
        else:
            messages.warning(request,'ERROR!!. Kindly please check the add address form')
            print(form.errors)
    else:
        form = AddressForm()
        
    context = {
        'form': form,
        'addresses':user_address,
    }
    return render(request,'usermanageaddress.html',context)


@login_required(login_url='userlogin')
@never_cache
def editAddress(request, address_id):
    
    address = get_object_or_404(Address, id=address_id, user=request.user , is_deleted=False)

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()  
            messages.success(request,"Address edited successfully")
            return redirect(reverse('userManageAddress'))  
        else:
            messages.warning(request,"Error in edititng the address")
            print(form.errors)
    else:
        form = AddressForm(instance=address) 
    context = {
        'form': form,
        'address': address,
    }
    return render(request, 'usereditaddress.html', context)


@login_required(login_url='userlogin')
@never_cache
def deleteAddress(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.is_deleted=True
    address.save()
    messages.success(request,'Address deleted Successfully')
    return redirect(reverse('userManageAddress'))



def addToWishlist(request):
    if request.method=="POST":
        product_id = request.POST.get('product_id')
        variant_id = request.POST.get('variant_id')
        
        product = get_object_or_404(Products,id=product_id)
        variant = get_object_or_404(Variant,id=variant_id)
        
        if request.user.is_authenticated:
            wishlist,created = Wishlist.objects.get_or_create(user=request.user)
        
            wishlist_item,item_created = WishlistItem.objects.get_or_create(wishlist=wishlist,product=product,variant=variant)    
            
            if item_created:
                messages.success(request,"Item added to wishlist!!!")
            else:
                messages.info(request,"This Items is already in your wishlist")
            return redirect(userWishlist)
        else:
            messages.error(request,"Please Login to add items to your cart!!")
            return redirect(userlogin)
        
    return redirect(userlogin)
            
            
def userWishlist(request):
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user=request.user).first()
        wishlist_item = wishlist.items.all() if wishlist else []
        
        return render(request,'userwishlist.html',{'wishlist_items':wishlist_item})
    
def removeFromWishlist(request,item_id):
    if request.user.is_authenticated:
        wishlist_item = get_object_or_404(WishlistItem,id=item_id,wishlist__user=request.user)
        wishlist_item.delete()
        messages.success(request,"Item remvoed form wishilist!!")
        return redirect(userWishlist)
    return redirect(userlogin)
        
    
                
    







@login_required(login_url='userlogin')
def addToCart(request):
    if request.method=="POST":
        product_id = request.POST.get('product_id')       
        variant_id = request.POST.get('variant_id')  
        print(variant_id)  
        quantity = request.POST.get('quantity')
   
        product = get_object_or_404(Products,id=product_id)
        product.popularity+=1
        product.save()
        variant = get_object_or_404(Variant,id=variant_id)
        
        if request.user.is_authenticated:
            cart,created = Cart.objects.get_or_create(user=request.user)
        
        
        cart_item,created = CartItem.objects.get_or_create(cart=cart,product=product,variant=variant,defaults={'quantity':1})
        if not created:
            cart_item.quantity += 1
        cart_item.save()
        return redirect(cartDetails)
    return redirect(productView)

@login_required(login_url='userlogin')
def cartDetails(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first() 
        cart_items = cart.items.select_related('product').prefetch_related('product__variants') if cart else []
        user_addresses = request.user.addresses.filter(is_deleted=False)

        available_coupons = Coupon.objects.filter(active=True)
        
        if user_addresses and not user_addresses.filter(is_primary=True).exists():
            first_address = user_addresses.first()
            first_address.is_primary = True
            first_address.save()
        
        is_cart_empty = not cart_items
        out_of_stock_items = []
        for item in cart_items:
            if item.quantity > item.variant.stock:  
                messages.warning(request, f"The quantity of {item.product.name} exceeds available stock.*Nos changed")
                item.quantity = item.variant.stock
                item.save()
            if item.variant.stock <= 0:
                out_of_stock_items.append(item)
        
            
        if out_of_stock_items:
            messages.warning(request, "Some items in your cart are out of stock. Please remove them to proceed.")    
        
        return render(request,'usercart.html',{
            'cart':cart,
            'cart_items':cart_items,
            'user_addresses':user_addresses,
            'out_of_stock_items': out_of_stock_items,
            'is_cart_empty':is_cart_empty,
            'available_coupons':available_coupons,
            })
    return render(request, 'usercart.html', {'cart': None, 'cart_items': [], 'user_addresses': []})



@login_required
def apply_coupon(request):
    if request.method == "POST":
        data = json.loads(request.body)
        coupon_id = data.get("coupon_id")
        remove = data.get('remove',False)
        cart = Cart.objects.filter(user=request.user).first()
        
        if not cart:
            return JsonResponse({"success": False, "error": "No active cart found."})
        
        if remove:
            # Remove coupon and reset discount
            cart.discount = 0
            cart.coupon = None
            cart.save()
            return JsonResponse({
                "success": True,
                "total_amount": cart.get_total_price(),
                "discounted_total": cart.get_discount_price(),
                "discount": 0,
                "removed": True  # Flag to indicate coupon removal
            })
    
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            print(coupon.is_valid())
            if not coupon.is_valid():
                return JsonResponse({'error': 'Coupon is expired or invalid'})
            
            usage_count = UserCoupon.objects.filter(user=request.user,coupon=coupon).count()
            if usage_count >= coupon.max_usage_per_person:
                return JsonResponse({'success':False,'error':f"This coupon has reached its usage limit of {coupon.max_usage_per_person} for your account."})
            
            if coupon.discount_amount:
                discount = coupon.discount_amount
            elif coupon.discount_percentage:
                discount = (coupon.discount_percentage/100) * cart.get_total_price()
                if coupon.max_discount_amount:
                    discount = min(discount,coupon.max_discount_amount)
            else:
                discount = 0
            
            if cart.get_total_price() < coupon.minimum_order_amount:
                return JsonResponse({'error': f'Minimum order amount of ₹{coupon.minimum_order_amount} is required'})
                     
            cart.discount = discount
            cart.coupon = coupon
            cart.save()
            
            return JsonResponse({
                "success": True,
                "total_amount": cart.get_total_price(),
                "discounted_total": cart.get_discount_price(),
                "discount":discount,
                "removed":False
                })
            
        except Coupon.DoesNotExist:
            return JsonResponse({"success": False, "error": "Invalid coupon code."})
    return JsonResponse({"success": False, "error": "Invalid request."})




@login_required(login_url='userlogin')
def removeCartItems(request,product_id,variant_id):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    
    
    if cart:
        cart_item = get_object_or_404(CartItem,cart=cart,product_id=product_id,variant_id=variant_id)
        cart_item.delete()
        return redirect(cartDetails)
    

@login_required(login_url='userlogin')
@csrf_exempt
def update_quantity(request):
    if request.user.is_authenticated:
       
        data = json.loads(request.body)
        product_id = data.get('product_id')
        variant_id = data.get('variant_id')
        quantity = data.get('quantity')

        cart = Cart.objects.filter(user=request.user).first()
        
        if cart:
           
            cart_item = cart.items.filter(product_id=product_id, variant_id=variant_id).first()
            variant = Variant.objects.filter(id=variant_id,product_id=product_id).first()
            
            if cart_item and variant:
                
                max_quantity = min(variant.stock,4)
                
                if quantity > max_quantity:
                    return JsonResponse({
                        'Success':False,
                        'error':f"Only {variant.stock} units of products are avaliable."
                    })
                
                if quantity > 4:
                    quantity = 4  
                
                cart_item.quantity = quantity
                cart_item.save()

                
                total_amount = sum(item.get_total_price() for item in cart.items.all())
                discounted_total = cart.get_discount_price()

                return JsonResponse({
                    'success': True,
                    'new_quantity': cart_item.quantity,
                    'total_amount': total_amount,
                    'discounted_total':discounted_total,
                })
            else:
                return JsonResponse({'success': False, 'error': 'Cart item does not exist.'})
        else:
            return JsonResponse({'success': False, 'error': 'Cart not found.'})

    return JsonResponse({'success': False, 'error': 'Invalid request.'})






@login_required(login_url='userlogin')
@csrf_exempt
def set_primary_address(request):
    if request.user.is_authenticated:
        data = json.loads(request.body)
        address_id = data.get('address_id')
        
        Address.objects.filter(user=request.user).update(is_primary=False)
        Address.objects.filter(id=address_id, user=request.user).update(is_primary=True)
        
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@login_required(login_url='userlogin')
@never_cache
def user_checkout(request):
   
    user_addresses = Address.objects.filter(user=request.user,is_deleted=False)
    payment_method = PaymentMethod.objects.all()
    
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
    except Cart.DoesNotExist:
        cart = None
        cart_items = []

    out_of_stock_items = []
    for item in cart_items:
        if item.quantity > item.variant.stock:
            out_of_stock_items.append(item)
    
    if out_of_stock_items:
        messages.warning(request, "Some items in your cart have insufficient stock. Please update your cart.")
        return redirect(cartDetails)  

    
    total_price = sum(item.get_total_price() for item in cart_items)
    # total_discount = sum(item.get_discount_amount() for item in cart_items)
    # shipping_fee = 0  # Assuming shipping is free for this example
    # final_total_price = total_price - total_discount + shipping_fee
    final_total_price = total_price

    
    context = {
        'user_addresses': user_addresses,
        'cart_items': cart_items,
        'cart': cart,
        'total_price': total_price,
        'final_total_price': final_total_price,
        'payment_methods':payment_method,
    }
    

    return render(request, 'usercheckout.html', context)



@login_required(login_url='userlogin')
@transaction.atomic
@never_cache
def placeOrder(request):
    if request.method == 'POST':
        try:
            print("Request Body:",request.body)
            data = json.loads(request.body)  
            user = request.user
            selected_address_id = data.get('address_id')
            payment_method_id = data.get('payment_method_id')
            print(selected_address_id)
            print(payment_method_id)
            cart = get_object_or_404(Cart, user=user)
            address = get_object_or_404(Address, id=selected_address_id, user=user)

            if not cart.items.exists():
                return JsonResponse({"error": "Your cart is empty"}, status=400)

            total_amount = cart.get_discount_price()
            print(total_amount)
            #sum(item.variant.price * item.quantity for item in cart.items.all())
            
            payment_method = get_object_or_404(PaymentMethod,id=payment_method_id)

            order = Order.objects.create(
                user=user,
                total_amount=total_amount,
                paymentmethod=payment_method,
                created_at=timezone.now(),
                address=address,
            )

            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    status="Shipped",
                    price=cart_item.variant.price
                )

                cart_item.variant.stock -= cart_item.quantity
                cart_item.variant.save()
            if cart.coupon:
                UserCoupon.objects.create(user=request.user,coupon=cart.coupon)
            
            cart.items.all().delete()
            cart.discount = 0
            cart.coupon = None
            cart.save()
            if payment_method.name.lower() == 'razorpay':
                print("inside razorpay in placeorder")
                return JsonResponse({"redirect_url": f"/initiate_payment/{order.id}/"}, status=200)

            
            order.is_paid = True
            order.save()
            return JsonResponse({"order_id": order.id}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Order placement failed: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@login_required(login_url='userlogin')
def initiate_payment(request,order_id):
    print("inside intiate_payment view")
    order = get_object_or_404(Order,id=order_id)
    
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    amount_in_paise = int(order.total_amount * 100)
    
    razorpay_order = client.order.create({
        "amount": amount_in_paise,
        "currency": "INR",
        "payment_capture": "1"
    })
    
    order.razorpay_payment_id = razorpay_order['id']
    order.save()
    
    context = {
        'order': order,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'total_amount': amount_in_paise,
    }
    return render(request, 'payment.html', context)
    

@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        print("inside payment_success view")

        try:
            order = Order.objects.get(razorpay_payment_id=razorpay_order_id)
            order.is_paid = True
            order.save()

            return JsonResponse({"status": "success", "message": "Payment successful"}, status=200)
        except Order.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Order not found"}, status=404)
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)







@login_required(login_url='userlogin')
def userYourOrder(request):
    user = request.user
    status_filter = request.GET.get('status', 'all') 
    
    if status_filter == 'all':
        orders = OrderItem.objects.filter(order__user=user).prefetch_related('product').order_by('-last_updated')
    else:
        orders = OrderItem.objects.filter(order__user=user, status=status_filter.capitalize()).prefetch_related('product').order_by('-last_updated')
        
    is_ajax_request = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    print("Is AJAX request:", is_ajax_request)
    
    if is_ajax_request:
        orders_html = render_to_string('partials/orders_list.html', {'orders': orders})
        return JsonResponse({'orders_html': orders_html})
    
    return render(request, 'user_your_order.html', {
        'orders': orders,
        'status_filter': status_filter
    })



@login_required(login_url='userlogin')
@require_POST
@csrf_exempt
@never_cache
def cancel_order_item(request, item_id):
    try:
        
        data = json.loads(request.body)
        reason = data.get('reason', '')

        
        order_item = OrderItem.objects.get(
        Q(status='Pending') | Q(status='Shipped'), 
        id=item_id, 
        order__user=request.user
        )
        
        
        order_item.status = 'Cancelled'
        order_item.cancellation_reason = reason
        order_item.save()
        
        variant = Variant.objects.filter(product=order_item.product).first()
        if variant:                    
            variant.stock += order_item.quantity          
            variant.save()
        else:
            pritn('variant not found')

        return JsonResponse({'success': True})
    except OrderItem.DoesNotExist:
        return JsonResponse({'success': False}, status=404)
    

@login_required(login_url='userlogin')
@require_POST
@csrf_exempt
@never_cache
def return_order_item(request, item_id):
    try:
        
        data = json.loads(request.body)
        reason = data.get('reason', '')

       
        order_item = OrderItem.objects.get(id=item_id, order__user=request.user, status='Delivered')

        
        order_item.status = 'Returned'
        order_item.return_reason = reason
        order_item.save()
        
        variant = Variant.objects.filter(product=order_item.product).first()
        if variant:
            variant.stock += order_item.quantity
            variant.save()
        else:
            print("variant not found")

        return JsonResponse({'success': True})
    except OrderItem.DoesNotExist:
        return JsonResponse({'success': False}, status=404)




@never_cache
@login_required(login_url='userlogin')
def userlogout(request):
    logout(request)
    print("logout succeessfully")
    return redirect('userlogin')
    # if request.user.is_authenticated:
    #     logout(request)
    #     print("sesssion destroyed")
    #     return redirect('userlogin')
    
    
    
        
    