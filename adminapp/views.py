from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import EuphoUser

# Create your views here.



def adminLogin(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect(adminCustomers)
        return render(request,'adminlogin.html')    
    return render(request,'adminlogin.html')

def checkAdmin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.warning(request,"Email and password are required")
            return render(request,'adminlogin.html')
        
        User = get_user_model()
        
        user = authenticate(request,email=email,password=password)
        if user:
            login(request,user)
            if user.is_staff:
                return redirect(adminLogin)
            else:
                messages.warning(request,'You do not have permission to admin site')
                return render(request,'adminlogin.html')
    else:
        messages.warning(request,"Invalid Credentials!")
        return render(request,'adminlogin.html')
    
    
def adminLogout(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            logout(request)
        return redirect(adminLogin)
    return redirect(adminLogin)
                
        

def adminCustomers(request):
    if request.user.is_superuser:
        user = EuphoUser.objects.all().order_by('id')
        return render(request,'admincustomers.html',{'users':user})
    return redirect(adminLogin)



User = get_user_model()
def blockUser(request,id):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            user = get_object_or_404(User,id=id)
            user.is_active = not user.is_active
            user.save()
            return redirect(adminCustomers)
        return render(request,'adminlogin.html')
    return render(request,'adminlogin.html')
            
    
def customerSearch(request):
    if request.method=='POST':
        search = request.POST.get('search')
        if search is not None:
            user = User.objects.filter(username__icontains=search).order_by('username')
        else:
            user = User.objects.all()
        return render(request,'adminCustomers.html',{'users':user})

def adminProducts(request):
    return render(request,'adminproducts.html')

def adminOrders(request):
    return render(request,'adminorders.html')
    
def adminCoupons(request):
    return render(request,'admincoupons.html')

