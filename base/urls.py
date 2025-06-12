from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('chat/<code>/', views.chat, name='chat'),
    path('create-room/', views.create_room, name='create_room'),
]