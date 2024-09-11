from django.urls import path
from . import views

urlpatterns = [
    path('mail/', views.mail_list, name='mail_list'),
]