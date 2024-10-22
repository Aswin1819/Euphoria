from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import EuphoUser,Category,Products,Images,Brand,Variant
from .forms import ProductForm, VariantForm

# Create your views here.

                                #########           #########
                                #########ADMIN LOGIN#########
                                #########           #########

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
                
        
        
                                #########           #########
                                #########ADMIN CUSTOMERS#####
                                #########           #########    
        
        
        
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


                    #########           #########
                    #########ADMIN CATEGORY######
                    #########           #########



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
        if request.user.is_authenticated:            
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



                            #########           #########
                            #########ADMIN PRODUCTS######
                            #########           #########





def adminProducts(request):
    if request.user.is_superuser:
        product = Products.objects.all().prefetch_related('variants').order_by('id')
        category = Category.objects.all()
        return render(request,'adminProducts.html',{'products':product,'categories':category})
    return redirect(adminLogin)


def addProducts(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            product_form = ProductForm(request.POST, request.FILES) 
            variant1_form = VariantForm(request.POST)

            image_files = [
                    request.FILES.get('image1'),
                    request.FILES.get('image2'),
                    request.FILES.get('image3'),
                    request.FILES.get('image4'),
                 ]
            
            if product_form.is_valid():
                product = product_form.save()
                
                for image_file in image_files:
                     if image_file:
                        Images.objects.create(images=image_file, product=product)
 
                if variant1_form.is_valid():
                    variant1 = variant1_form.save(commit=False)
                    variant1.product = product
                    variant1.save()
                else:
                    print(variant1_form.errors)

                messages.success(request, "Product and variants added successfully")
                return redirect('adminProducts')
            else:
                messages.warning(request, "Please correct the errors below.")
        else:
            product_form = ProductForm()
            variant1_form = VariantForm()

    categories = Category.objects.all()
    brands = Brand.objects.all()
    return render(request, 'addproducts.html', {
        'product_form': product_form,
        'variant1_form': variant1_form,
        'categories': categories,
        'brands': brands,
    })




def editProducts(request, id):
    if request.user.is_superuser:
        product = get_object_or_404(Products, id=id)
        variant =   product.variants.first()
        product_form = ProductForm(instance=product)
        variant1_form = VariantForm(instance=variant) 

        if request.method == 'POST':
            product_form = ProductForm(request.POST, request.FILES, instance=product)  
            variant1_form = VariantForm(request.POST,instance=variant)
            
            if product_form.is_valid() and variant1_form.is_valid():
                product = product_form.save()

                # Handle image uploads
                uploaded_images = [
                    request.FILES.get('image1'),
                    request.FILES.get('image2'),
                    request.FILES.get('image3'),
                    request.FILES.get('image4')
                ]

                for index, image_file in enumerate(uploaded_images):
                    if image_file:
                       
                        existing_image = product.product_images.all()[index] if product.product_images.all().count() > index else None
                        if existing_image:
                            existing_image.images = image_file
                            existing_image.save()
                        else:
                            new_image = Images.objects.create(images=image_file, product=product)
                            product.product_images.add(new_image)  

                
                variant1 = variant1_form.save(commit=False)
                variant1.product = product
                variant1.save()

                messages.success(request, "Product edited successfully.")
                return redirect('adminProducts')
            else:
                messages.warning(request, "Please correct the errors below.")
                print(product_form.errors)
                print(variant1_form.errors)
                
        categories = Category.objects.all()
        brands = Brand.objects.all()
        images = product.product_images.all()  
        return render(request, 'editProducts.html', {
            'product_form': product_form,
            'variant1_form': variant1_form,
            'categories': categories,
            'brands': brands,
            'images': images,
        })
    return redirect('adminLogin')


def productSearch(request):
    if request.user.is_superuser:
        if request.method=='POST':
            search = request.POST.get('search')
            if search:
                product = Products.objects.filter(name__icontains=search).order_by('name')
            else:
                product = Products.objects.all()
            return render(request,'adminproducts.html',{'products':product})
            
def removeProducts(request,id):
    if request.user.is_superuser:
        if request.user.is_authenticated:
            if request.method=='POST':
                product = get_object_or_404(Products,id=id)
                product.is_active = not product.is_active
                product.save()
                return redirect(adminProducts)
            else:
                print("request method is not post")
        else:
            print("user is not authenticated")    
    return redirect(adminLogout)


                    #########           #########
                    #########ADMIN BRANDS########
                    #########           #########



def adminBrands(request):
    if request.user.is_superuser:
        brand = Brand.objects.all().order_by('id')
        return render(request,'adminbrands.html',{'items':brand})
    return redirect(adminLogin)


def addBrands(request):
    if request.user.is_superuser:
        if request.method=='POST':
            brand = request.POST.get('brand')
            new_brand=Brand.objects.create(name=brand)
            new_brand.save()
            return redirect(adminBrands)
    return redirect(adminLogin)


def removeBrands(request,id):
    if request.user.is_superuser:
        brand = Brand.objects.get(id=id)
        brand.is_active = not brand.is_active
        brand.save()
        return redirect(adminBrands)
    return redirect(adminLogin)


def editBrands(request,id):
    if request.user.is_superuser:
        if request.method=='POST':
            new_name = request.POST.get('brand')
            brand = Brand.objects.get(id=id)
            brand.name=new_name
            brand.save()
            return redirect(adminBrands)
    return redirect(adminLogin)
        

def brandSearch(request):
    if request.user.is_superuser:
        if request.method=='POST':
            search = request.POST.get('search')
            if search is not None:
                item = Brand.objects.filter(name__icontains=search).order_by('name')
            else:
                item = Brand.objects.all()
            return render(request,'adminbrands.html',{'items':item})









 
def adminOrders(request):
    return render(request,'adminorders.html')
    
def adminCoupons(request):
    return render(request,'admincoupons.html')

