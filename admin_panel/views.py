from django.views.decorators.cache import cache_control
from accounts.models import User
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from .forms import AdminLoginForm
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required


def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)  # Use 'username=email'
            if user is not None:
                if user.is_admin:
                    request.session['is_admin'] = True  # Set session variable
                    return redirect('user_data')  # Redirect to the admin dashboard
                else:
                    messages.error(request, 'You are not authorized to access this page.')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = AdminLoginForm()

    return render(request, 'adminside/admin_login.html', {'form': form})


#

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def user_data(request):
    if not request.session.get('is_admin'):
        return redirect('admin-login')

    users = User.objects.filter(is_admin=False)
    return render(request, 'adminside/user_data.html', {'users': users})

def block_user(request, user_id):
    if not request.session.get('is_admin'):
        # logger.debug("Admin not logged in, redirecting to admin-login")
        return redirect('admin-login')

    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        user.is_active = False
        user.save()
        messages.success(request, f'User {user.username} has been blocked.')
        # logger.debug(f"User {user.username} has been blocked")
    return redirect('user_data')

def unblock_user(request, user_id):
    if not request.session.get('is_admin'):
        # logger.debug("Admin not logged in, redirecting to admin-login")
        return redirect('admin-login')

    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        user.is_active = True
        user.save()
        messages.success(request, f'User {user.username} has been unblocked.')
        # logger.debug(f"User {user.username} has been unblocked")
    return redirect('user_data')

def admin_logout(request):
    if request.session.get('is_admin'):
        del request.session['is_admin']
        messages.success(request, 'You have been logged out successfully.')
        # logger.debug("Admin logged out successfully")
    # else:
    #     logger.debug("No admin session found to log out")
    return redirect('admin-login')


def admin_dashboard(request):
    return render(request, 'adminside/dashboard.html')