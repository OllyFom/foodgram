from django.urls import path

from recipes.views import redirect_short_link

urlpatterns = [
    path(
        's/<str:short_code>/',
        redirect_short_link,
        name='redirect_short_link',
    ),
]
