from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    paginator = Paginator(products, 10)  # Show 10 products per page
    page = request.GET.get('page')
    
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    
    # Attach discount_percentage to each product
    for product in products_page:
        if product.price and product.discounted_price and product.discounted_price > product.price:
            product.discount_percentage = ((product.price - product.discounted_price) / product.price) * 100
        else:
            product.discount_percentage = None
    
    return render(request, 'products/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products_page,
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    specifications_list = product.specifications.split(',') if product.specifications else []
    product.discount_percentage = ((product.price - product.discounted_price) / product.price) * 100
    context = {
        'product': product,
        'specifications_list': specifications_list,
    }
    return render(request, 'products/product_detail.html', context)

def product_list_by_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all()
    return render(request, 'products/product_list.html', {'products': products, 'categories': categories, 'current_category': category})