from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.hashers import make_password
from adminapp.models import EuphoUser,OTP,Products,Variant,Address,Cart,CartItem,Order,OrderItem
from decimal import Decimal
from django.contrib import messages
from userapp.userotp import generateAndSendOtp
from django.conf import settings
from .signals import userOtpVerified
from .forms import UserLoginForm,UserSignupForm,ChangeProfileForm,ChangePasswordForm,AddressForm
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

# Create your views here.



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


def resendotp(request):
    if request.method =='POST':
        email = request.POST.get('email')
        
        otp = generateAndSendOtp(email)
        OTP.objects.create(email=email,otp=otp)
        
        messages.success(request,"A new OTP has send to your email")
        return render(request,'otp_validation.html',{'email':email})
    return render(request,'otp_validation.html')

def resendOtpForPass(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        otp = generateAndSendOtp(email)
        OTP.objects.create(email=email,otp=otp)
        
        messages.success(request,'A new OTP send to your email')
        return render(request,'forg_pass_otp.html',{'email':email})
    return render(request,'forg_pass_otp.html')



def forgPassEmailVerification(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            if EuphoUser.objects.filter(email=email).exists():
                otp = generateAndSendOtp(email)
                OTP.objects.create(email=email,otp=otp)
                # return render(request,'forg_pass_otp.html',{'email':email})
                return render(request,'forg_pass_otp.html',{'email':email})
            else:
                messages.warning(request,'email not exist')
        except:
            messages.warning(request,"Enter your email")
            return render(request,'forg_pass_email.html')        
        
    return render(request,'forg_pass_email.html')


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



def changePassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmPassword = request.POST.get('confirm_password')
        
        if password and confirmPassword and password==confirmPassword:
            try:
                user = EuphoUser.objects.get(email=email)
                user.set_password(password)
                user.save()
                messages.success(request,'Password Succeessfully changed!!')
                return redirect('userlogin')
            except EuphoUser.DoesNotExist:
                messages.warning(request,"User does not exist")
        else:
            messages.warning(request,"Password not match or are empty")
            return render(request,'change_password.html',{'email':email})
    
    return render(request,'change_password.html')

def userhome(request):
    products = Products.objects.filter(category__is_active=True,brand__is_active=True).prefetch_related('variants')[15:27]
    latest_product = Products.objects.filter(category__is_active=True,brand__is_active=True).order_by('-id')[:4]
    featured = Products.objects.filter(is_featured=True,category__is_active=True,brand__is_active=True)
    return render(request,'user_home.html',{'products':products,'latest_products':latest_product,'featured_products':featured})

def shopNow(request):
    products = Products.objects.filter(category__is_active=True,brand__is_active=True).prefetch_related('variants')
    return render(request,'shopnow.html',{'products':products})

def productView(request,id):
    product = get_object_or_404(Products, id=id)
    variants = Variant.objects.filter(product=product)
    default_variant = variants.first() if variants else None
    related_products = Products.objects.filter(brand=product.brand,category__is_active=True,brand__is_active=True).exclude(id=product.id)
    return render(request,'productview.html',{'product':product,'related_products':related_products,'variants':variants,'default_variant':default_variant})


# def userProfile(request):
#     if request.user.is_authenticated:
#         user = request.user
#         if request.method=='POST': 
#             form = ChangeProfileForm(request.POST,request.FILES,instance=user)
#             if form.is_valid():
#                 form.save()
#                 return render(request,'userprofile.html',{'form':form})
#             else:
#                 print(form.errors)
#         else:
#             form = ChangeProfileForm(instance=user)
#     return render(request,'userprofile.html',{'form':form})



# @login_required
# def changePasswordProfile(request):
#     user=request.user
#     if request.method == 'POST':
#         form = ChangePasswordForm(user = request.user,data=request.POST)
#         if form.is_valid():
#             form.save()
#             update_session_auth_hash(request,form.user)#updating the session
#             print("password changed successfully")
#             return redirect(userProfile)
#         else:
#             print(form.errors)
#     else:
#         form = ChangePasswordForm(instance=user)
#     return render(request,'userprofile.html',{'form':form})       

@login_required
def userProfileInformation(request):
    user = request.user

    # Handle profile form
    profile_form = ChangeProfileForm(instance=user)
    
    # Handle password form
    password_form = ChangePasswordForm(user=user)

    if request.method == 'POST':
        # Check which form is being submitted
        if 'profile_submit' in request.POST:
            profile_form = ChangeProfileForm(request.POST, request.FILES, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                print("profile edited successfully")
                return redirect('userProfileInformation')
            else:
                print(profile_form.errors)

        elif 'password_submit' in request.POST:
            password_form = ChangePasswordForm(user=user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)  # Keeps the user logged in
                print("Password changed successfully")
                return redirect('userProfileInformation')
            else:
                print(password_form.errors)

    return render(request, 'userprofileinformation.html', {
        'profile_form': profile_form,
        'password_form': password_form,
    })
    
        

def userManageAddress(request):
    
    user_address = Address.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user=request.user
            address.save()
            return redirect(userManageAddress)
        else:
            print(form.errors)
    else:
        form = AddressForm()
        
    context = {
        'form': form,
        'addresses':user_address,
    }
    return render(request,'usermanageaddress.html',context)



@login_required
def editAddress(request, address_id):
    # Get the address object for the given ID and user
    address = get_object_or_404(Address, id=address_id, user=request.user)

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()  # Update the existing address
            return redirect(reverse('userManageAddress'))  # Redirect back to the address management page
    else:
        form = AddressForm(instance=address)  # Populate form with existing data

    context = {
        'form': form,
        'address': address,
    }
    return render(request, 'usereditaddress.html', context)

@login_required
def deleteAddress(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    return redirect(reverse('userManageAddress'))



def addToCart(request):
    if request.method=="POST":
        product_id = request.POST.get('product_id')       
        variant_id = request.POST.get('variant_id')    
        quantity = request.POST.get('quantity')
   
        product = get_object_or_404(Products,id=product_id)
        variant = get_object_or_404(Variant,id=variant_id)
        
        if request.user.is_authenticated:
            cart,created = Cart.objects.get_or_create(user=request.user)
        else:
            cart,created = Cart.objects.get_or_create(session_id=request.session.session_key)
        
        cart_item,created = CartItem.objects.get_or_create(cart=cart,product=product,variant=variant,defaults={'quantity':1})
        if not created:
            cart_item.quantity += 1
        cart_item.save()
        return redirect(cartDetails)
    return redirect(productView)


def cartDetails(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first() 
        cart_items = cart.items.select_related('product').prefetch_related('product__variants') if cart else []
        user_addresses = request.user.addresses.all() 
        if user_addresses and not user_addresses.filter(is_primary=True).exists():
            first_address = user_addresses.first()
            first_address.is_primary = True
            first_address.save()
            
        return render(request,'usercart.html',{'cart':cart,'cart_items':cart_items,'user_addresses':user_addresses})
    return render(request, 'usercart.html', {'cart': None, 'cart_items': [], 'user_addresses': []})


def removeCartItems(request,product_id,variant_id):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        cart = Cart.objects.filter(session_id=request.session.session_key).first()
    
    if cart:
        cart_item = get_object_or_404(CartItem,cart=cart,product_id=product_id,variant_id=variant_id)
        cart_item.delete()
        return redirect(cartDetails)
    


# @csrf_exempt
# def update_quantity(request):
#     if request.user.is_authenticated:
#         data = json.loads(request.body)
#         product_id = data.get('product_id')
#         variant_id = data.get('variant_id')
#         quantity = data.get('quantity')
        
#         cart = Cart.objects.filter(user=request.user).first()
#         cart_item = cart.items.filter(product_id=product_id, variant_id=variant_id).first()
#         cart_item.quantity = quantity
#         cart_item.save()
        
#         total_amount = sum(item.get_total_price() for item in cart.items.all())
#         return JsonResponse({'success': True, 'new_quantity': cart_item.quantity, 'total_amount': total_amount})
#     return JsonResponse({'success': False})

@csrf_exempt
def update_quantity(request):
    if request.user.is_authenticated:
        # Extract data from the request body
        data = json.loads(request.body)
        product_id = data.get('product_id')
        variant_id = data.get('variant_id')
        quantity = data.get('quantity')

        # Retrieve the user's cart
        cart = Cart.objects.filter(user=request.user).first()
        
        if cart:
            # Get the cart item
            cart_item = cart.items.filter(product_id=product_id, variant_id=variant_id).first()
            
            if cart_item:
                # Enforce the max quantity rule on the server side
                if quantity > 4:
                    quantity = 4  # Cap it at 4 if somehow bypassed on the client side

                # Update quantity and save
                cart_item.quantity = quantity
                cart_item.save()

                # Calculate the new total for display
                total_amount = sum(item.get_total_price() for item in cart.items.all())

                return JsonResponse({
                    'success': True,
                    'new_quantity': cart_item.quantity,
                    'total_amount': total_amount
                })
            else:
                return JsonResponse({'success': False, 'error': 'Cart item does not exist.'})
        else:
            return JsonResponse({'success': False, 'error': 'Cart not found.'})

    return JsonResponse({'success': False, 'error': 'Invalid request.'})

@csrf_exempt
def set_primary_address(request):
    if request.user.is_authenticated:
        data = json.loads(request.body)
        address_id = data.get('address_id')
        
        Address.objects.filter(user=request.user).update(is_primary=False)
        Address.objects.filter(id=address_id, user=request.user).update(is_primary=True)
        
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})




# def setPrimaryAddress(request,address_id):
#     if request.user.is_authenticated:
#         Address.objects.filter(user=request.user,is_primary=True).update(is_primary=False)
        
#         selected_address = get_object_or_404(Address,id=address_id,user=request.user)
#         selected_address.is_primary=True
#         selected_address.save()
#     return redirect(cartDetails)


def user_checkout(request):
   
    user_addresses = Address.objects.filter(user=request.user)
    
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
    except Cart.DoesNotExist:
        cart = None
        cart_items = []

    
    total_price = sum(item.get_total_price() for item in cart_items)
    # total_discount = sum(item.get_discount_amount() for item in cart_items)
    # shipping_fee = 0  # Assuming shipping is free for this example
    # final_total_price = total_price - total_discount + shipping_fee
    final_total_price = total_price

    # Context to pass to the template
    context = {
        'user_addresses': user_addresses,
        'cart_items': cart_items,
        'cart': cart,
        'total_price': total_price,
        'final_total_price': final_total_price,
    }
    
    # 'total_discount': total_discount,
    #     'shipping_fee': shipping_fee,

    return render(request, 'usercheckout.html', context)


# @login_required
# @transaction.atomic
# def placeOrder(request):
#     if request.method == 'POST':
#         user = request.user
#         selected_address_id = request.POST.get('address_id')
#         payment_method = request.POST.get('payment_method')
        
#         cart = get_object_or_404(Cart, user=user)
#         address = get_object_or_404(Address,id=selected_address_id,user=user)
        
#         if not cart.items.exists():
#             return JsonResponse({"error":"Your cart is empty"},status=400)
        
#         total_amount = sum(item.variant.price * item.quantity for item in cart.items.all())
        
#         order = Order.objects.create(
#             user=user,
#             total_amount=total_amount,
#             status="Pending",
#             created_at=timezone.now()
#         )
        
#         for cart_item in cart.items.all():
#             OrderItem.objects.create(
#                 order=order,
#                 product=cart_item.product,
#                 quantity=cart_item.quantity,
#                 price=cart_item.variant.price
#             )
            
#             cart_item.variant.stock -= cart_item.quantity
#             cart_item.save()
            
#         cart.items.all().delete()
#         return JsonResponse({"order_id": order.id}, status=200)
#     return JsonResponse({"error": "Invalid request method"}, status=405)


@login_required
@transaction.atomic
def placeOrder(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Parse JSON data
            user = request.user
            selected_address_id = data.get('address_id')
            payment_method = data.get('payment_method')

            cart = get_object_or_404(Cart, user=user)
            address = get_object_or_404(Address, id=selected_address_id, user=user)

            if not cart.items.exists():
                return JsonResponse({"error": "Your cart is empty"}, status=400)

            total_amount = sum(item.variant.price * item.quantity for item in cart.items.all())

            order = Order.objects.create(
                user=user,
                total_amount=total_amount,
                status="Pending",
                payment_method=payment_method,
                created_at=timezone.now()
            )

            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.variant.price
                )

                cart_item.variant.stock -= cart_item.quantity
                cart_item.variant.save()

            cart.items.all().delete()
            return JsonResponse({"order_id": order.id}, status=200)

        except Exception as e:
            return JsonResponse({"error": f"Order placement failed: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)




@login_required
def userYourOrder(request):
    user = request.user
    status_filter = request.GET.get('status', 'all')  # Get the status filter from the URL, default to 'all'

    # Retrieve orders based on the status filter
    if status_filter == 'all':
        orders = Order.objects.filter(user=user)
    else:
        orders = Order.objects.filter(user=user, status=status_filter.capitalize())
        
    is_ajax_request = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    print("Is AJAX request:", is_ajax_request)
    
    if is_ajax_request:
        orders_html = render_to_string('partials/orders_list.html', {'orders': orders})
        return JsonResponse({'orders_html': orders_html})
    
    
    # if request.headers.get('x-requested-with') == 'XMLHttpRequest':
    #     orders_html = render_to_string('partials/orders_list.html', {'orders': orders})
    #     return JsonResponse({'orders_html': orders_html})

    # Render the template with orders and the current filter
    return render(request, 'user_your_order.html', {
        'orders': orders,
        'status_filter': status_filter
    })




@require_POST
@csrf_exempt
def cancel_order(request, order_id):
    try:
        # Parse JSON request body to get the cancellation reason
        data = json.loads(request.body)
        reason = data.get('reason', '')

        order = Order.objects.get(id=order_id, user=request.user, status='Pending')
        order.status = 'Cancelled'
        order.cancellation_reason = reason  # Save cancellation reason
        order.save()
        return JsonResponse({'success': True})
    except Order.DoesNotExist:
        return JsonResponse({'success': False}, status=404)
    


@require_POST
@csrf_exempt
def return_order(request, order_id):
    try:
        # Parse JSON request body to get the cancellation reason
        data = json.loads(request.body)
        reason = data.get('reason', '')

        order = Order.objects.get(id=order_id, user=request.user, status='Delivered')
        order.status = 'Returned'
        order.return_reason = reason  # Save cancellation reason
        order.save()
        return JsonResponse({'success': True})
    except Order.DoesNotExist:
        return JsonResponse({'success': False}, status=404)
















def userlogout(request):
    logout(request)
    print("logout succeessfully")
    return redirect('userlogin')
    # if request.user.is_authenticated:
    #     logout(request)
    #     print("sesssion destroyed")
    #     return redirect('userlogin')
    
    
    
        
    