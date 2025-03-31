from django.contrib import admin
from django.urls import path, include
from api.views.recipes import redirect_short_link

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),

    path('api/', include('api.urls')),
    path('s/<str:short_code>/', redirect_short_link, name='short-link-redirect'),
]
