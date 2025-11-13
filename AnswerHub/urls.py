from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('questions/', permanent=False)),
    path('admin/', admin.site.urls),
    path('questions/', include('questions.urls')),
    path('users/', include('users.urls')),
    path('answers/', include('answers.urls')),
    path('tags/', include('tags.urls')),
    path('search/', include('search.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
