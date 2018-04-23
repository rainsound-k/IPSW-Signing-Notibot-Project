from django.contrib import admin
from django.urls import path

from ipsw_search.views import keyboard, answer

urlpatterns = [
    path('admin/', admin.site.urls),
    path('keyboard/', keyboard),
    path('message', answer),
]
