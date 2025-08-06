from django.shortcuts import render, redirect
from django.conf import settings
from .models import *
from .forms import PhoneForm, OTPForm
from twilio.rest import Client
import random
import razorpay

# Twilio OTP
def send_otp(phone, otp):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=f"Your BEVCO OTP is: {otp}",
        from_=settings.TWILIO_PHONE,
        to=phone
    )

# Home - list products
def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})

# Login with phone
def login_phone(request):
    if request.method == 'POST':
        form = PhoneForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            otp = str(random.randint(1000, 9999))
            customer, created = Customer.objects.get_or_create(phone=phone)
            customer.otp = otp
            customer.save()
            send_otp(phone, otp)
            request.session['phone'] = phone
            return redirect('verify_otp')
    else:
        form = PhoneForm()
    return render(request, 'login_phone.html', {'form': form})

# OTP verification
def verify_otp(request):
    phone = request.session.get('phone')
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            customer = Customer.objects.get(phone=phone)
            if customer.otp == entered_otp:
                customer.is_verified = True
                customer.save()
                request.session['user_id'] = customer.id
                return redirect('home')
    else:
        form = OTPForm()
    return render(request, 'verify_otp.html', {'form': form})

# Buy product
def buy(request, product_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login_phone')
    customer = Customer.objects.get(id=user_id)
    product = Product.objects.get(id=product_id)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
    order = client.order.create({
        "amount": int(product.price * 100),
        "currency": "INR",
        "payment_capture": 1
    })

    new_order = Order.objects.create(
        customer=customer,
        product=product,
        razorpay_order_id=order['id']
    )

    context = {
        'product': product,
        'order': order
    }
    return render(request, 'buy.html', context)

# Payment success
def payment_success(request):
    if request.method == "POST":
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')

        try:
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
            order.paid = True
            order.razorpay_payment_id = razorpay_payment_id
            order.save()
        except:
            pass
    return render(request, 'success.html')
