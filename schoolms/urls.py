from django.contrib import admin
from django.urls import path, include
from core.admin import admin_site

urlpatterns = [
    path("admin/", admin_site.urls),
    path("", include("core.urls")),
]

from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
