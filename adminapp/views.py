from django.shortcuts import render

# Create your views here.



def adminLogin(request):
    return render(request,'adminlogin.html')

def adminCustomers(request):
    return render(request,'admincustomers.html')


def adminProducts(request):
    return render(request,'adminproducts.html')

def adminOrders(request):
    return render(request,'adminorders.html')
    
def adminCoupons(request):
    return render(request,'admincoupons.html')

