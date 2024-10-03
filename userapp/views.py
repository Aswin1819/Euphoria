from django.shortcuts import render

# Create your views here.

def userLogin(request):
    return render(request,'userlogin.html')

def userSignup(request):
    return render(request,'usersignup.html')

def forgPassEmailVerification(request):
    return render(request,'forg_pass_email.html')

def otpValidation(request):
    return render(request,'otp_validation.html')

def changePassword(request):
    return render(request,'change_password.html')