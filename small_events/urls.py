from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from small_events import views

urlpatterns = [
    path('create/', views.create_event),
]