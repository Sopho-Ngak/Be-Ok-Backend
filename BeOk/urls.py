
from django.contrib import admin
from django.urls import path, include
# import django settings
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


urlpatterns = [
    path('dashboard', admin.site.urls),
    path('', include('patients.urls')),
    path('', include('accounts.urls')),
    path('', include('doctors.urls')),
    path('', include('chats.urls')),
    path('', include('settings.urls')),
    path('', include('hospital.urls')),
    path('beok/api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('beok/api/ui/', SpectacularSwaggerView.as_view(url_name='schema'),
         name='swagger-ui'),
    path('beok/api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc')
]

# add static files
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# add media files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
