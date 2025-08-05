"""
URL configuration for theopendecor project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

def home_redirect(request):
    """Redirect home page to login"""
    return redirect('login')

def ignore_request(request):
    """Ignore development tool requests"""
    return HttpResponse(status=204)  # No Content

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_redirect, name='home'),
    path('', include('users.urls')),
    path('leads/', include('leads.urls')),
    # Ignore development tool requests
    path('__reload__/events/', ignore_request, name='ignore_reload'),
    path('.well-known/appspecific/com.chrome.devtools.json', ignore_request, name='ignore_devtools'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
