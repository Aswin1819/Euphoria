from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import EuphoUser,Category,Products,Images,Brand

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
                brand_id = request.POST.get('product_brand')
                stock = request.POST.get('quantity')
                price = request.POST.get('price')
                weight = request.POST.get('weight')
                
                image_files = [
                    request.FILES.get('image1'),
                    request.FILES.get('image2'),
                    request.FILES.get('image3'),
                    request.FILES.get('image4')
                ]
                
                if not all([name,description,category_id,brand_id,stock,price,weight]+image_files):
                    messages.warning(request,"All fileds are reuired")
                    return render(request,'addproducts.html')
                try:
                    price = float(price)
                    stock = int(stock)
                except ValueError:
                    messages.warning(request,"Invalid price or stock value")
                    return render(request,'addproducts.html')
                    
                category = Category.objects.get(id = category_id)
                brand = Brand.objects.get(id = brand_id)
                
                product = Products.objects.create(
                    name = name,
                    description = description,
                    price = price,
                    stock = stock,
                    brand = brand,
                    category = category,
                    weight = weight,
                    
                 )
                
                for image_file in image_files:
                    if image_file:
                        Images.objects.create(images=image_file, product=product)
                
                messages.success(request,"Product added Successfully")
                return redirect(adminProducts)     
                               
            except Exception as e:
                messages.warning(request,f"Error in adding products {str(e)}")
                return render(request,'addproducts.html')
            
    categories = Category.objects.all()     
    brands = Brand.objects.all()
    return render(request,'addproducts.html',{'categories':categories,'brands':brands})

def editProducts(request, id):
    if request.user.is_superuser:
        product = get_object_or_404(Products, id=id)

        if request.method == 'POST':
            try:
                name = request.POST.get('product_name')
                description = request.POST.get('description')
                category_id = request.POST.get('category_name')
                brand_id = request.POST.get('product_brand')
                stock = request.POST.get('quantity')
                price = request.POST.get('price')
                weight = request.POST.get('weight')

                # Validate inputs
                if not all([name, description, category_id, brand_id, stock, price]):
                    messages.warning(request, "All fields except weight are required.")
                    return render(request, 'editProducts.html', {'product': product})

                try:
                    price = float(price)
                    stock = int(stock)
                except ValueError:
                    messages.warning(request, "Invalid price or stock value.")
                    return render(request, 'editProducts.html', {'product': product})

                category = Category.objects.get(id=category_id)
                brand = Brand.objects.get(id=brand_id)

                # Update product details
                product.name = name
                product.description = description
                product.price = price
                product.stock = stock
                product.weight = weight
                product.category = category
                product.brand = brand
                product.save()

                # Handling image upload
                uploaded_images = [
                    request.FILES.get('image1'),
                    request.FILES.get('image2'),
                    request.FILES.get('image3'),
                    request.FILES.get('image4')
                ]

                for index, image_file in enumerate(uploaded_images):
                    if image_file:
                        # If a new image is uploaded, create or replace it
                        existing_image = product.product_images.all()[index] if product.product_images.all().count() > index else None
                        if existing_image:
                            existing_image.images = image_file
                            existing_image.save()
                        else:
                            new_image = Images.objects.create(images=image_file, product=product)
                            product.product_images.add(new_image)

                messages.success(request, "Product edited successfully.")
                return redirect(adminProducts)

            except Exception as e:
                messages.warning(request, f"Error in editing product: {str(e)}")
                return render(request, 'editProducts.html', {'product': product})

        # Render the edit page with product details
        categories = Category.objects.all()
        brands = Brand.objects.all()
        images = product.product_images.all()  # Use the related name `product_images`

        return render(request, 'editProducts.html', {
            'categories': categories,
            'images': images,
            'product': product,
            'brands': brands
        })

    return redirect(adminLogin)


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
        product = Products.objects.get(id=id)
        product.is_active = not product.is_active
        product.save()
        return redirect(adminProducts)
    return redirect(adminLogin)



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

