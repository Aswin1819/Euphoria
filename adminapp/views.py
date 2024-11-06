from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import EuphoUser,Category,Products,Images,Brand,Variant,Order,OrderItem
from .forms import ProductForm, VariantForm
from django.forms import modelformset_factory
from django.db.models import Q
from django.contrib.auth.decorators import login_required
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
        
        
@login_required(login_url='adminLogin')
def adminCustomers(request):
    if request.user.is_superuser:
        user = EuphoUser.objects.all().order_by('-updated_at')
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
            
    
@login_required(login_url='adminLogin')
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


@login_required(login_url='adminLogin')
def adminCategory(request):
    if request.user.is_superuser:
        category = Category.objects.all().order_by('-updated_date')
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
            messages.success(request,'Category edited successfully')
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




@login_required(login_url='userlogin')
def adminProducts(request):
    if request.user.is_superuser:
        product = Products.objects.all().prefetch_related('variants').order_by('-updated_at')
        category = Category.objects.all()
        return render(request,'adminProducts.html',{'products':product,'categories':category})
    return redirect(adminLogin)


def addProducts(request):
    if request.user.is_superuser:
        VariantFormSet = modelformset_factory(Variant,form=VariantForm,extra=2)
        if request.method == 'POST':
            product_form = ProductForm(request.POST, request.FILES) 
            variant_formset = VariantFormSet(request.POST)
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




# def editProducts(request,id):
#     if request.user.is_superuser:
#         # Retrieve the product to be edited
#         product = Products.objects.get(id=id)
#         VariantFormSet = modelformset_factory(Variant, form=VariantForm, extra=0)  # No extra forms unless necessary
        
#         if request.method == 'POST':
#             product_form = ProductForm(request.POST,instance=product)
#             variant_formset = VariantFormSet(request.POST, queryset=Variant.objects.filter(product=product))
#             image_files = [
#                 request.POST.get('image1'),
#                 request.POST.get('image2'),
#                 request.POST.get('image3'),
#                 request.POST.get('image4'),
#             ]
          
                           
#             if product_form.is_valid():
#                 updated_product = product_form.save()
#                 print('product and variant forms are valid')
#                 # Update or replace images if new ones are uploaded
#                 for index, image_data in enumerate(image_files):
#                     if image_data:
#                         try:
#                             print('inside image try block')
#                             format, imgstr = image_data.split(';base64,')
#                             ext = format.split('/')[-1]
#                             image_file = ContentFile(base64.b64decode(imgstr), name=f'product_image_{index+1}.{ext}')
                            
#                             # Update existing image or create new if no image exists at that index
#                             if index < updated_product.product_images.count():
#                                 existing_image = updated_product.product_images.all()[index]
#                                 existing_image.images = image_file
#                                 existing_image.save()
#                             else:
#                                 Images.objects.create(images=image_file, product=updated_product)
#                         except Exception as e:
#                             print(f"Error processing image: {e}")
#                     else:
#                         print(f"No image provided for image{index+1}")
                
#                 # Update the variants
#                 variants = variant_formset.save(commit=False)
#                 for variant in variants:
#                     variant.product = updated_product
#                     variant.save()

#                 # Delete removed variants if necessary
#                 for variant in variant_formset.deleted_objects:
#                     variant.delete()

#                 messages.success(request, "Product and variants updated successfully")
#                 return redirect('adminProducts')
#             else:
#                 print(product_form.errors)
#                 print('inside the else of validation')
#                 messages.warning(request, "Please correct the errors below.")
#         else:
#             product_form = ProductForm(instance=product)
#             variant_formset = VariantFormSet(queryset=Variant.objects.filter(product=product))

#         categories = Category.objects.all()
#         brands = Brand.objects.all()

#         return render(request, 'editproducts.html', {
#             'product_form': product_form,
#             'variant_formset': variant_formset,
#             'categories': categories,
#             'brands': brands,
#             'product': product,  # Pass the product to prepopulate the form
#         })

#     return redirect(adminLogin)

def editProducts(request, id):
    if request.user.is_superuser:
        product = get_object_or_404(Products, id=id)
        VariantFormSet = modelformset_factory(Variant, form=VariantForm, extra=0, can_delete=True)
        
        if request.method == 'POST':
            product_form = ProductForm(request.POST,instance=product)
            variant_formset = VariantFormSet(request.POST, queryset=product.variants.all())

            image_files = [
                request.POST.get('image1'),
                request.POST.get('image2'),
                request.POST.get('image3'),
                request.POST.get('image4'),
            ]

            if product_form.is_valid() and variant_formset.is_valid():
                updated_product = product_form.save()
                
                # Handle images
                for index, image_data in enumerate(image_files):
                    if image_data:
                        try:
                            format, imgstr = image_data.split(';base64,')
                            ext = format.split('/')[-1]
                            image_file = ContentFile(base64.b64decode(imgstr), name=f'product_image_{index+1}.{ext}')
                            
                            if index < updated_product.product_images.count():
                                # Update existing image
                                existing_image = updated_product.product_images.all()[index]
                                existing_image.images = image_file
                                existing_image.save()
                            else:
                                # Add new image if less than 4 exist
                                Images.objects.create(images=image_file, product=updated_product)
                        except Exception as e:
                            print(f"Error processing image: {e}")
                    else:
                        print("There is no vlaid image")
                            

                # Handle variants
                # variants = variant_formset.save(commit=False)
                for form in variant_formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        form.save()
                    elif form.cleaned_data.get('DELETE', False) and form.instance.pk:
                        form.instance.delete()

                messages.success(request, "Product and variants updated successfully.")
                return redirect('adminProducts')
            else:
                # Log form and formset errors
                print("Product Form Errors:", product_form.errors)
                print("Variant Formset Errors:", variant_formset.errors)
                messages.warning(request, "Please correct the errors below.")
        
        else:
            product_form = ProductForm(instance=product)
            variant_formset = VariantFormSet(queryset=Variant.objects.filter(product=product))

        return render(request, 'editproducts.html', {
            'product_form': product_form,
            'variant_formset': variant_formset,
            'product': product,
        })

    return redirect('adminLogin')



def addVariant(request):
    if request.method == 'POST':
        form = VariantForm(request.POST)
        product_id = request.POST.get('product_id')
        if form.is_valid():
            variant = form.save(commit=False)  
            # product_id = request.POST.get('product_id') 
            try:
                product = Products.objects.get(id=product_id) 
                variant.product = product 
                variant.save()  
                messages.success(request, "Variant added successfully.")
            except Products.DoesNotExist:
                messages.error(request, "The product does not exist.")
            return redirect('adminProducts')  
        else:
            print("form is not valid")
            messages.warning(request,'The Price and Weight must be postive numbers')
            return redirect('adminProducts')
    else:
        form = VariantForm()  # Create a new form instance for a GET request

    return render(request, 'adminproducts.html', {'form': form})




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
        brand = Brand.objects.all().order_by('-updated_date')
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









@login_required(login_url='adminLogin')
def adminOrders(request):
    if request.user.is_superuser:     
        orders = OrderItem.objects.select_related('order', 'product').prefetch_related('order__user').order_by('-last_updated')
        return render(request, 'adminorders.html', {'orders': orders})
    else:
        return redirect(adminLogin)


def UpdateOrderStatus(request, order_item_id):
    if request.method == 'POST':
        order_item = get_object_or_404(OrderItem, id=order_item_id)
        new_status = request.POST.get('status')
        order_item.status = new_status
        order_item.save()
        return redirect(adminOrders)


def orderSearch(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            search = request.POST.get('search')
            if search:
                result = OrderItem.objects.filter(
                    Q(product__name__icontains=search) | 
                    Q(order__user__username__icontains=search)
                ).distinct()  

                return render(request, 'adminorders.html', {'orders': result, 'search_query': search})
    return render(request, 'adminorders.html', {'orders': []})
            
                


def adminCoupons(request):
    return render(request,'admincoupons.html')

