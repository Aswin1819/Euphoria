from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.hashers import make_password
from adminapp.models import EuphoUser,OTP
from django.contrib import messages
from userapp.userotp import generateAndSendOtp
from django.conf import settings
from .signals import userOtpVerified

# Create your views here.



def userlogin(request):
    if request.user.is_authenticated:
        return redirect('userhome')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.warning(request,"email and password are required")
            return redirect('userlogin')
        user = authenticate(request,username=email,password=password)
        print(user)
        # x = EuphoUser.objects.get(email=email)
        # print(x.email)
        # print(x.password)
        if user:
            login(request,user)
            return redirect('userhome')
        else:
            messages.warning(request,"Invalid username or password")
            return render(request,"userlogin.html")
         
    return render(request,"userlogin.html")


def usersignup(request):
    if request.user.is_authenticated:
        return redirect('userhome')
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validation
        if not username or not email or not password or not confirm_password:
            messages.warning(request, 'All fields are required')
            return redirect(usersignup)
        
        if EuphoUser.objects.filter(username=username).exists():
            messages.warning(request, 'Username already exists')
            return redirect(usersignup)
        
        if not (email.endswith('.com') and email[0].isalpha()):
            messages.warning(request, 'Enter a valid email')
            return redirect(usersignup)
        
        if EuphoUser.objects.filter(email=email).exists():
            messages.warning(request, 'Email is already registered')
            return redirect(usersignup)

        if len(password) < 8:
            messages.warning(request, 'Password must be at least 8 characters')
            return redirect(usersignup)
        
        if password != confirm_password:
            messages.warning(request, 'Passwords do not match')
            return redirect(usersignup)

        # Use EuphoUser to create a new user
        new_user = EuphoUser.objects.create_user(
            username=username,
            email=email,
            phone=phone,
            password=password,
        )
        new_user.save()
        
        # Send OTP
        otp = generateAndSendOtp(email)
        OTP.objects.create(email=email, otp=otp)
        
        messages.success(request, 'OTP sent to your email. Please validate.')
        return render(request, 'otp_validation.html', {'email': email})
    
    return render(request, 'usersignup.html')





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
        print("zero")

        try:
            # Get the OTP record associated with the email and the full OTP
            print("hello")
            otpRecord = OTP.objects.get(email=email,otp=otp)
            print("one")
            # Assuming `is_valid()` checks for expiry
            if otpRecord.is_valid():
                # Trigger OTP verified signal
                print("two")
                
                userOtpVerified.send(sender=OTP, email=email)
                print("three")
                
                # Delete only OTPs for this email (safer than deleting all)
                OTP.objects.filter(email=email).delete()
                
                messages.success(request, "OTP verified. Create New Password")
                return render(request, 'change_password.html', {'email': email})
            else:
                messages.warning(request, "OTP has expired")
        except OTP.DoesNotExist:
            print("out")
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
    return render(request,'user_home.html')

def userlogout(request):
    logout(request)
    return redirect('userlogin')
    # if request.user.is_authenticated:
    #     logout(request)
    #     print("sesssion destroyed")
    #     return redirect('userlogin')
    
    
    
        
    