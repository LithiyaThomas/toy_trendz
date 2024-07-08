from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
import random
from .forms import RegisterForm, LoginForm
from .models import User
from django.contrib.auth import authenticate, login
from django.utils import timezone
from dateutil.parser import parse
from .models import Address
from .forms import AddressForm
from django.contrib.auth.decorators import login_required
# Generate a random OTP
def generate_otp():
    return random.randint(100000, 999999)


# User login view
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['username']  # Get email from the username field
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, 'Invalid email or password')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


# User registration view
def user_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account until it is confirmed

            otp = generate_otp()
            send_mail(
                "Your OTP Code",
                f"Your OTP code is {otp}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],

            )
            # Store the OTP in the session
            request.session['otp'] = str(otp)
            request.session['user_data'] = form.cleaned_data
            request.session['otp_creation_time'] = timezone.now().isoformat()
            return redirect('verify_otp')  # Redirect to the OTP verification page
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


# OTP verification view
def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get('entered_otp')
        otp = request.session.get('otp')
        otp_creation_time = request.session.get('otp_creation_time')
        user_data = request.session.get('user_data')

        if not otp or not otp_creation_time:
            messages.error(request, 'OTP not found or expired. Please try registering again.')
            return redirect('user_register')

        otp_creation_time = parse(otp_creation_time)
        if (timezone.now() - otp_creation_time).total_seconds() > 120:
            messages.error(request, 'OTP expired. Please resend OTP.')
            return redirect('verify_otp')

        if entered_otp == otp:
            user = User.objects.create_user(
                full_name=user_data['full_name'],
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                phone=user_data['phone'],
                # Add other fields as necessary
            )
            user.is_active = True
            user.save()

            backend = 'accounts.backends.EmailBackend'  # Or whichever backend you prefer
            user.backend = backend
            login(request, user, backend=backend)

            # Clear session data
            request.session.pop('otp', None)
            request.session.pop('otp_creation_time', None)
            request.session.pop('user_data', None)
            return redirect('home')
        else:
            messages.error(request, 'Invalid OTP')

    otp_creation_time = request.session.get('otp_creation_time')
    otp_expiration_time = parse(otp_creation_time) + timezone.timedelta(seconds=120)
    return render(request, 'accounts/otp_verify.html', {'otp_expiration_time': otp_expiration_time.isoformat() })


def resend_otp(request):
    user_data = request.session.get('user_data')

    if not user_data:
        messages.error(request, 'User data not found. Please try registering again.')
        return redirect('user_register')

    otp = generate_otp()
    send_mail(
        "Your OTP Code",
        f"Your new OTP code is {otp}",
        settings.DEFAULT_FROM_EMAIL,
        [user_data['email']],
    )

    request.session['otp'] = str(otp)
    request.session['otp_creation_time'] = timezone.now().isoformat()

    messages.success(request, 'A new OTP has been sent to your email.')
    return redirect('verify_otp')


def home(request):
    return render(request, 'accounts/home.html')


@login_required
def create_address(request):
    next_url = request.GET.get('next', None)

    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            if request.POST.get('is_default') == 'on':
                address.is_default = True
                Address.objects.filter(user=request.user).exclude(id=address.id).update(is_default=False)
            address.save()
            if next_url:
                return redirect(next_url)
            else:
                return redirect('home')
    else:
        form = AddressForm()

    return render(request, 'accounts/create_address.html', {'form': form})


@login_required
def edit_address(request, address_id):
    next_url = request.GET.get('next', None)

    address = get_object_or_404(Address, id=address_id, user=request.user)

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            address = form.save(commit=False)
            if request.POST.get('is_default') == 'on':
                address.is_default = True
                Address.objects.filter(user=request.user).exclude(id=address.id).update(is_default=False)
            address.save()
            if next_url:
                return redirect(next_url)
            else:
                return redirect('home')
    else:
        form = AddressForm(instance=address)

    return render(request, 'accounts/edit_address.html', {'form': form, 'address': address})


@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)

    if request.method == 'POST':
        address.delete()
        return redirect('home')

    return render(request, 'accounts/delete_address.html', {'address': address})