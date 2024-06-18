from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
import random
from .forms import RegisterForm, LoginForm
from .models import User
from django.contrib.auth import authenticate, login
from django.utils import timezone
from dateutil.parser import parse

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
                return redirect(settings.LOGIN_REDIRECT_URL)  # Use the LOGIN_REDIRECT_URL from settings
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
            user.save()

            otp = generate_otp()
            send_mail(
                "Your OTP Code",
                f"Your OTP code is {otp}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )
            # Store the OTP in the session
            request.session['otp'] = str(otp)
            request.session['user_id'] = user.id
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

        if not otp or not otp_creation_time:
            messages.error(request, 'OTP not found or expired. Please try registering again.')
            return redirect('user_register')

        otp_creation_time = parse(otp_creation_time)
        if (timezone.now() - otp_creation_time).total_seconds() > 300:  # Example: 5 minutes
            messages.error(request, 'OTP expired. Please try registering again.')
            return redirect('user_register')

        if entered_otp == otp:
            user_id = request.session.get('user_id')
            if not user_id:
                messages.error(request, 'User ID not found in session. Please try registering again.')
                return redirect('user_register')

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                messages.error(request, 'User not found. Please try registering again.')
                return redirect('user_register')

            # Activate the user and log them in
            user.is_active = True
            user.save()

            backend = 'accounts.backends.EmailBackend'  # Or whichever backend you prefer
            user.backend = backend
            login(request, user, backend=backend)

            # Clear session data
            request.session.pop('otp', None)
            request.session.pop('otp_creation_time', None)
            request.session.pop('user_id', None)

            return redirect('home')
        else:
            messages.error(request, 'Invalid OTP')

    return render(request, 'accounts/otp_verify.html')

# Home view
def home(request):
    return render(request, 'accounts/home.html')
