from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import EuphoUser,Category,Products,Images,Brand,Variant,Order,OrderItem
from .forms import ProductForm, VariantForm
from django.forms import modelformset_factory
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.cache import never_cache
#imagecropping modules
from django.core.files.base import ContentFile
import base64
import re

# Create your views here.

                                #########           #########
                                #########ADMIN LOGIN#########
                                #########           #########
@never_cache
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
    
        
@never_cache
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
        user_list = EuphoUser.objects.all().order_by('-updated_at')
        
        paginator = Paginator(user_list,5)
        page_number = request.GET.get('page')
        user = paginator.get_page(page_number)
        
        return render(request,'admincustomers.html',{'users':user})
    return redirect(adminLogin)


User = get_user_model()
@never_cache
def blockUser(request,id):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            user = get_object_or_404(User,id=id)
            user.is_active = not user.is_active
            user.save()
            return redirect(adminCustomers)
        return render(request,'adminlogin.html')
    return render(request,'adminlogin.html')
            

@never_cache
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
        category_list = Category.objects.all().order_by('-updated_date')
        
        paginator = Paginator(category_list,5)
        page_number = request.GET.get('page')
        category = paginator.get_page(page_number)
        
        return render(request,'admincategory.html',{'items':category})
    return redirect(adminLogin)


@never_cache
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

@never_cache
def removeCategory(request,id):
    if request.user.is_superuser:
        if request.user.is_authenticated:            
            item = Category.objects.get(id=id)
            item.is_active = not item.is_active
            item.save()
            return redirect(adminCategory)
        
    return redirect(adminLogin)


@never_cache
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


@never_cache
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



@never_cache
@login_required(login_url='userlogin')
def adminProducts(request):
    if request.user.is_superuser:
        product_list = Products.objects.all().prefetch_related('variants').order_by('-updated_at')
        category = Category.objects.all()
        
        paginator = Paginator(product_list,5)
        page_number = request.GET.get('page')
        product = paginator.get_page(page_number)
        
        return render(request,'adminProducts.html',{'products':product,'categories':category})
    return redirect(adminLogin)


@never_cache
def addProducts(request):
    if request.user.is_superuser:
        VariantFormSet = modelformset_factory(Variant,form=VariantForm,extra=1)
        
        if request.method == 'POST':
            product_form = ProductForm(request.POST) #request.FILES changed
            variant_formset = VariantFormSet(request.POST)
            
            image_files = [
                    request.POST.get('image1'),
                    request.POST.get('image2'),
                    request.POST.get('image3'),
                    request.POST.get('image4'),
                 ]
            
            if product_form.is_valid() and variant_formset.is_valid():
                print("form and variants are valid ")
                product = product_form.save()
                
                for image_data in image_files:
                    if image_data:  
                        try:
                            format, imgstr = image_data.split(';base64,')
                            ext = format.split('/')[-1]  
                            image_file = ContentFile(base64.b64decode(imgstr), name=f'product_image.{ext}')
                            Images.objects.create(images=image_file, product=product)
                        except Exception as e:
                            print(f"Error processing image: {e}")
                    else:
                        print("No image provided or invalid image.")

                
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
            variant_formset = VariantFormSet(queryset=Variant.objects.none())

        categories = Category.objects.all()
        brands = Brand.objects.all()
        return render(request, 'addproducts.html', {
            'product_form': product_form,
            'variant_formset': variant_formset,
            'categories': categories,
            'brands': brands,
        })
    return redirect(adminLogin)


@never_cache
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
                existing_images = updated_product.product_images.all()
                for index, image_data in enumerate(image_files):
                    if image_data:
                        try:
                            format, imgstr = image_data.split(';base64,')
                            ext = format.split('/')[-1]
                            image_file = ContentFile(base64.b64decode(imgstr), name=f'product_image_{index+1}.{ext}')
                            if index < len(existing_images):
                                existing_image = existing_images[index]
                                existing_image.images = image_file
                                existing_image.save()
                            else:
                                Images.objects.create(images=image_file, product=updated_product)
                        except Exception as e:
                            print(f"Error processing image: {e}")
                            

                # Handle variants
                for form in variant_formset:
                    if form.cleaned_data:
                        if form.cleaned_data.get('DELETE', False):
                            if form.instance.pk:
                                form.instance.delete()
                        else:
                            form.save()

                messages.success(request, "Product and variants updated successfully.")
                return redirect('adminProducts')
            else:
                print("Product Form Errors:", product_form.errors)
                print("Variant Formset Errors:", variant_formset.errors)
                messages.warning(request, "Please correct the errors below.")
        
        else:
            product_form = ProductForm(instance=product)
            variant_formset = VariantFormSet(queryset=product.variants.all())

        return render(request, 'editproducts.html', {
            'product_form': product_form,
            'variant_formset': variant_formset,
            'product': product,
        })

    return redirect('adminLogin')


@never_cache
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



@never_cache
def productSearch(request):
    if request.user.is_superuser:
        if request.method=='POST':
            search = request.POST.get('search')
            if search:
                product = Products.objects.filter(name__icontains=search).order_by('name')
            else:
                product = Products.objects.all()
                
            return render(request,'adminproducts.html',{'products':product})


@never_cache
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
        brand_list = Brand.objects.all().order_by('-updated_date')
        
        paginator = Paginator(brand_list,5)
        page_number = request.GET.get('page')
        brand = paginator.get_page(page_number)
        
        return render(request,'adminbrands.html',{'items':brand})
    return redirect(adminLogin)

@never_cache
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


@never_cache
def removeBrands(request,id):
    if request.user.is_superuser:
        brand = Brand.objects.get(id=id)
        brand.is_active = not brand.is_active
        brand.save()
        return redirect(adminBrands)
    return redirect(adminLogin)

@never_cache
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
        

@never_cache
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
        orders_list = OrderItem.objects.select_related('order', 'product').prefetch_related('order__user').order_by('-last_updated')
        
        paginator = Paginator(orders_list,5)
        page_number = request.GET.get('page')
        orders = paginator.get_page(page_number)
        
        return render(request, 'adminorders.html', {'orders': orders})
    else:
        return redirect(adminLogin)


@never_cache
def UpdateOrderStatus(request, order_item_id):
    if request.method == 'POST':
        order_item = get_object_or_404(OrderItem, id=order_item_id)
        new_status = request.POST.get('status')
        order_item.status = new_status
        order_item.save()
        return redirect(adminOrders)


@never_cache
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

