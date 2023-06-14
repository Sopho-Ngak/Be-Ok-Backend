
from django.contrib import admin
from django.urls import path, include
# import django settings
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('patients.urls')),
    path('', include('accounts.urls')),
]

# add static files
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# add media files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
