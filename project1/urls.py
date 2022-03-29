from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('profile/', include('profiles.urls')),
    path('orders/', include('orders.urls')),
    path('admin/', admin.site.urls),
]
