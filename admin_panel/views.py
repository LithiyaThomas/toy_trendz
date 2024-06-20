import logging
from django.shortcuts import render, redirect
from .forms import AdminLoginForm
from django.views.decorators.cache import cache_control
from accounts.models import User
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.conf import settings

logger = logging.getLogger(__name__)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_login(request):
    predefined_admin_username = settings.ADMIN_USERNAME
    predefined_admin_password = settings.ADMIN_PASSWORD

    if request.session.get('is_admin'):
        logger.debug("Admin already logged in, redirecting to user_data")
        return redirect('user_data')

    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            if username == predefined_admin_username and password == predefined_admin_password:
                request.session['is_admin'] = True
                logger.debug("Admin login successful, redirecting to user_data")
                return redirect('user_data')
            else:
                messages.error(request, 'Invalid username or password.')
                logger.debug("Invalid login credentials")
    else:
        form = AdminLoginForm()

    return render(request, 'adminside/admin_login.html', {'form': form})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_data(request):
    if not request.session.get('is_admin'):
        logger.debug("Admin not logged in, redirecting to admin-login")
        return redirect('admin-login')

    users = User.objects.all()
    logger.debug("Rendering user_data page")
    return render(request, 'adminside/user_data.html', {'users': users})

def block_user(request, user_id):
    if not request.session.get('is_admin'):
        logger.debug("Admin not logged in, redirecting to admin-login")
        return redirect('admin-login')

    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        user.is_active = False
        user.save()
        messages.success(request, f'User {user.username} has been blocked.')
        logger.debug(f"User {user.username} has been blocked")
    return redirect('user_data')

def unblock_user(request, user_id):
    if not request.session.get('is_admin'):
        logger.debug("Admin not logged in, redirecting to admin-login")
        return redirect('admin-login')

    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        user.is_active = True
        user.save()
        messages.success(request, f'User {user.username} has been unblocked.')
        logger.debug(f"User {user.username} has been unblocked")
    return redirect('user_data')

def admin_logout(request):
    if request.session.get('is_admin'):
        del request.session['is_admin']
        messages.success(request, 'You have been logged out successfully.')
        logger.debug("Admin logged out successfully")
    else:
        logger.debug("No admin session found to log out")
    return redirect('admin-login')

def admin_dashboard(request):

    return render(request, 'adminside/dashboard.html')