from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import Product

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")

    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out")
    return redirect('login')


@login_required
def dashboard(request):
    return render(request, 'accounts/dashboard.html')

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully")
            return redirect('login')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def profile_view(request):
    return render(request,'accounts/profile.html')
    
from django.shortcuts import redirect, render

def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})

    product_id = str(product_id)  # session এ key সবসময় string রাখা safe

    if product_id in cart:
        cart[product_id] += 1     # quantity বাড়বে
    else:
        cart[product_id] = 1      # নতুন item

    request.session['cart'] = cart
    return redirect('cart')


def remove_cart(request, product_id):
    cart = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session['cart'] = cart
    return redirect('cart')


from .models import Product

def cart_view(request):
    cart = request.session.get('cart', {})
    products = []
    total = 0

    for product_id, quantity in cart.items():
        product = Product.objects.filter(id=product_id).first()

        if product:   # product exists কিনা check
            product.quantity = quantity
            product.subtotal = product.price * quantity
            total += product.subtotal
            products.append(product)

    return render(request, 'accounts/cart.html', {
        'products': products,
        'total': total
    })





def product_list(request):
    products=Product.objects.all()
    return render(request, 'accounts/products.html', {'products': products})