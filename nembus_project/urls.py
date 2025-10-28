# nembus_project/urls.py

from django.contrib import admin
from django.urls import path, include
# --- Imports añadidos ---
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('nembus_app.urls')),
]

# --- LÍNEAS AÑADIDAS AL FINAL ---
# Esto le dice a Django que sirva los archivos de la carpeta /media/
# solo cuando estamos en modo de depuración (DEBUG=True).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)