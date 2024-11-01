from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import EuphoUser,Category,Products,Images,Brand,Variant,Order,OrderItem
from .forms import ProductForm, VariantForm
from django.forms import modelformset_factory
#imagecropping modules
from django.core.files.base import ContentFile
import base64
import re
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
            if Category.objects.filter(name__iexact=category).exists():
                messages.warning(request,"Category name already exists")
                return redirect(adminCategory)
            if not category:
                messages.warning(request,"name cant be empty")
                return redirect(adminCategory)
            if not re.match("^[A-Za-z ]*$", category) or not category.strip():
                messages.warning(request, "Name must contain only letters and cannot be empty.")
                return redirect(adminCategory)
            
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
            if Category.objects.filter(name__iexact=new_name).exclude(id=id).exists():
                messages.warning(request,"Category name already exists")
                return redirect(adminCategory)
            if not new_name:
                messages.warning(request,"name cant be empty")
                return redirect(adminCategory)
            if not re.match("^[A-Za-z ]*$", new_name) or not new_name.strip():
                messages.warning(request, "Name must contain only letters and cannot be empty.")
                return redirect(adminCategory)
            
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
        VariantFormSet = modelformset_factory(Variant,form=VariantForm,extra=2)
        if request.method == 'POST':
            # print("Form Data:", request.POST) 
            product_form = ProductForm(request.POST, request.FILES) 
            # variant1_form = VariantForm(request.POST)
            variant_formset = VariantFormSet(request.POST)
            # print("Product Form is bound:", product_form.is_bound)
            # print("Variant Formset is bound:", variant_formset.is_bound)

            image_files = [
                    request.POST.get('image1'),
                    request.POST.get('image2'),
                    request.POST.get('image3'),
                    request.POST.get('image4'),
                 ]
            # print(image_files[0])
            
            if product_form.is_valid() and variant_formset.is_valid():
                print("form and variants are valid ")
                product = product_form.save()
                
                # for image_file in image_files:
                #      if image_file:
                #         Images.objects.create(images=image_file, product=product)
                
                for image_data in image_files:
                    if image_data:  # Ensure that there is base64 data
                        try:
                            format, imgstr = image_data.split(';base64,')
                            ext = format.split('/')[-1]  # Extract file extension
                            image_file = ContentFile(base64.b64decode(imgstr), name=f'product_image.{ext}')
                            Images.objects.create(images=image_file, product=product)
                        except Exception as e:
                            print(f"Error processing image: {e}")
                    else:
                        print("No image provided or invalid image.")

                
                #saving each variant in formset
                
                variants = variant_formset.save(commit=False)
                for variant in variants:
                    variant.product = product
                    variant.save()
 
                # if variant1_form.is_valid():
                #     variant1 = variant1_form.save(commit=False)
                #     variant1.product = product
                #     variant1.save()
                # else:
                #     print(variant1_form.errors)

                messages.success(request, "Product and variants added successfully")
                return redirect('adminProducts')
            else: 
                print("Product Form Errors:", product_form.errors)
                print("Variant Formset Errors:", variant_formset.errors)
                messages.warning(request, "Please correct the errors below.")
        else:
            product_form = ProductForm()
            # variant1_form = VariantForm()
            variant_formset = VariantFormSet(queryset=Variant.objects.none())

    categories = Category.objects.all()
    brands = Brand.objects.all()
    return render(request, 'addproducts.html', {
        'product_form': product_form,
        'variant_formset': variant_formset,
        'categories': categories,
        'brands': brands,
    })




def editProducts(request,id):
    if request.user.is_superuser:
        # Retrieve the product to be edited
        product = Products.objects.get(id=id)
        VariantFormSet = modelformset_factory(Variant, form=VariantForm, extra=0)  # No extra forms unless necessary
        
        if request.method == 'POST':
            product_form = ProductForm(request.POST,instance=product)
            variant_formset = VariantFormSet(request.POST, queryset=Variant.objects.filter(product=product))
            image_files = [
                request.POST.get('image1'),
                request.POST.get('image2'),
                request.POST.get('image3'),
                request.POST.get('image4'),
            ]
            # print(image_files[0])
            
            if product_form.is_valid() and variant_formset.is_valid():
                updated_product = product_form.save()

                # Update or replace images if new ones are uploaded
                for index, image_data in enumerate(image_files):
                    if image_data:
                        try:
                            format, imgstr = image_data.split(';base64,')
                            ext = format.split('/')[-1]
                            image_file = ContentFile(base64.b64decode(imgstr), name=f'product_image_{index+1}.{ext}')
                            
                            # Update existing image or create new if no image exists at that index
                            if index < updated_product.product_images.count():
                                existing_image = updated_product.product_images.all()[index]
                                existing_image.images = image_file
                                existing_image.save()
                            else:
                                Images.objects.create(images=image_file, product=updated_product)
                        except Exception as e:
                            print(f"Error processing image: {e}")
                    else:
                        print(f"No image provided for image{index+1}")
                
                # Update the variants
                variants = variant_formset.save(commit=False)
                for variant in variants:
                    variant.product = updated_product
                    variant.save()

                # Delete removed variants if necessary
                for variant in variant_formset.deleted_objects:
                    variant.delete()

                messages.success(request, "Product and variants updated successfully")
                return redirect('adminProducts')
            else:
                print(product_form.errors)
                print(variant_formset.errors)
                print('inside the else of validation')
                messages.warning(request, "Please correct the errors below.")
        else:
            product_form = ProductForm(instance=product)
            variant_formset = VariantFormSet(queryset=Variant.objects.filter(product=product))

        categories = Category.objects.all()
        brands = Brand.objects.all()

        return render(request, 'editproducts.html', {
            'product_form': product_form,
            'variant_formset': variant_formset,
            'categories': categories,
            'brands': brands,
            'product': product,  # Pass the product to prepopulate the form
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
            if not brand:
                messages.warning(request,"Name cant be empty")
                return redirect(adminBrands)
            if Brand.objects.filter(name__iexact=brand).exists():
                messages.warning(request,"Brand name already exists")
                return redirect(adminBrands)
            if not re.match("^[A-Za-z ]*$", brand) or not brand.strip():
                messages.warning(request, "Name must contain only letters and cannot be empty.")
                return redirect(adminCategory)
            
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
            if not new_name:
                messages.warning(request,"Name cant be empty")
                return redirect(adminBrands)
            if Brand.objects.filter(name__iexact=new_name).exclude(id=id).exists():
                messages.warning(request,"Brand name already exists")
                return redirect(adminBrands)
            if not re.match("^[A-Za-z ]*$", new_name) or not new_name.strip():
                messages.warning(request, "Name must contain only letters and cannot be empty.")
                return redirect(adminCategory)
            
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
    orders = Order.objects.select_related('user').prefetch_related('order_items__product')
    return render(request,'adminorders.html',{'orders':orders})


def UpdateOrderStatus(request,order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order,id=order_id)
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()
        return redirect(adminOrders)



def adminCoupons(request):
    return render(request,'admincoupons.html')

