from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import EuphoUser,Category,Products,Images

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
            if user is not None:
                login(request,user)
                if user.is_staff:
                    return redirect(adminLogin)
                else:
                    messages.warning(request,'You do not have permission to admin site')
                    return render(request,'adminlogin.html')
            else:
                messages.warning(request,"Invalid Email or Password")
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


def adminCategory(request):
    if request.user.is_superuser:
        category = Category.objects.all().order_by('id')
        return render(request,'admincategory.html',{'items':category})
    return redirect(adminLogin)

def addCategory(request):
    if request.user.is_superuser:
        if request.method == "POST":
            category = request.POST.get('category')
            new_category = Category.objects.create(name=category)
            new_category.save()
            print("category added successfully")
            return redirect(adminCategory)
    return redirect(adminLogin)

def removeCategory(request,id):
    if request.user.is_superuser:
        item = Category.objects.get(id=id)
        item.is_active = not item.is_active
        item.save()
        return redirect(adminCategory)
    return redirect(adminLogin)

def editCategory(request,id):
    if request.user.is_superuser:
        if request.method=='POST':
            new_name = request.POST.get('category')
            
            item = Category.objects.get(id=id)
            item.name = new_name
            item.save()
            return redirect(adminCategory)
    return redirect(adminLogin)

def categorySearch(request):
    if request.user.is_superuser:
        if request.method=='POST':
            search = request.POST.get('search')
            if search is not None:
                item = Category.objects.filter(name__icontains=search).order_by('name')
            else:
                item = Category.objects.all()
            return render(request,'admincategory.html',{'items':item})


def adminProducts(request):
    if request.user.is_superuser:
        product = Products.objects.all().order_by('id')
        category = Category.objects.all()
        return render(request,'adminProducts.html',{'products':product,'categories':category})
    return redirect(adminLogin)

def addProducts(request):
    if request.user.is_superuser:
        if request.method=='POST':
            try:
                name = request.POST.get('product_name')
                description = request.POST.get('description')
                category_id = request.POST.get('category_name')
                brand = request.POST.get('product_brand')
                stock = request.POST.get('quantity')
                price = request.POST.get('price')
                
                
                image1 = request.FILES.get('image1')
                image2 = request.FILES.get('image2')
                image3 = request.FILES.get('image3')
                image4 = request.FILES.get('image4')
                
                if not all([name,description,category_id,brand,stock,price]):
                    messages.warning(request,"All fileds are reuired")
                    return render(request,'addproducts.html')
                try:
                    price = float(price)
                    stock = int(stock)
                except ValueError:
                    messages.warning(request,"Invalid price or stock value")
                    return render(request,'addproducts.html')
                    
                category = Category.objects.get(id = category_id)
                
                product = Products.objects.create(
                    name = name,
                    description = description,
                    price = price,
                    stock = stock,
                    brand = brand,
                    category = category,
                    
                 )
                
                for image_file in [image1,image2,image3,image4]:
                    if image_file:
                        image_instance = Images.objects.create(images = image_file)
                        product.images.add(image_instance) 
                
                messages.success(request,"Product added Successfully")
                return redirect(adminProducts)
                
                                    
            except Exception as e:
                messages.warning(request,f"Error in adding products {str(e)}")
                return render(request,'addproducts.html')
    categories = Category.objects.all()     
    return render(request,'addproducts.html',{'categories':categories})

def editProducts(request,id):
    if request.user.is_superuser:
        product = get_object_or_404(Products,id=id)
        if request.method=='POST':
            name = request.POST.get('product_name')
            description = request.POST.get('description')
            category_id = request.POST.get('category_name')
            brand = request.POST.get('product_brand')
            stock = request.POST.get('quantity')
            price = request.POST.get('price')
                
                
            image1 = request.FILES.get('image1')
            image2 = request.FILES.get('image2')
            image3 = request.FILES.get('image3')
            image4 = request.FILES.get('image4')
                
            category = Category.objects.get(id=category_id)
                
            product.name = name
            product.description = description
            product.price = price
            product.stock = stock
            product.category = category
            product.brand = brand

            product.save()
            print("product saved successfully")   
            
            uploaded_images = [image1, image2, image3, image4] 
            for image_file in uploaded_images:
                image = Images(images=image_file)
                image.save()
                product.images.add(image)
                product.save()
                
            messages.success(request,"product edited successfully")
            return redirect(adminProducts) 
        categories = Category.objects.all()
        images = product.images.all()
        return render(request,'editProducts.html',{'categories':categories,'images':images,'product':product})
    return redirect(adminLogin)

def adminOrders(request):
    return render(request,'adminorders.html')
    
def adminCoupons(request):
    return render(request,'admincoupons.html')

