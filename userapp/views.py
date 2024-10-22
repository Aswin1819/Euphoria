from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.hashers import make_password
from adminapp.models import EuphoUser,OTP,Products,Variant
from django.contrib import messages
from userapp.userotp import generateAndSendOtp
from django.conf import settings
from .signals import userOtpVerified
from .forms import UserLoginForm,UserSignupForm

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
    products = Products.objects.filter(category__is_active=True,brand__is_active=True).prefetch_related('variants')
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


def userProfile(request):
    if request.user.is_authenticated:
        return render(request,'userprofile.html')
    else:
        return redirect(userlogin)
    
    
        
    
        










def userlogout(request):
    logout(request)
    print("logout succeessfully")
    return redirect('userlogin')
    # if request.user.is_authenticated:
    #     logout(request)
    #     print("sesssion destroyed")
    #     return redirect('userlogin')
    
    
    
        
    