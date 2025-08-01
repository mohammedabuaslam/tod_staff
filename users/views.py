from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpRequest, HttpResponse

def login_view(request: HttpRequest) -> HttpResponse:
    """Custom login view for user authentication"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please provide both username and password.')
    
    return render(request, 'users/login.html')

@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    """Dashboard view for authenticated users"""
    context = {
        'user': request.user,
        'title': 'Dashboard - The Open Decor'
    }
    return render(request, 'users/dashboard.html', context)

def logout_view(request: HttpRequest) -> HttpResponse:
    """Custom logout view that handles both GET and POST requests"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')
