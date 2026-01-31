from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include("raffle.admin_urls")),
    path("", include("raffle.urls")),
]
