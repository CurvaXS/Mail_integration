from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('mail/', views.mail_list, name='mail_list'),
    path('mail/<int:pk>/', views.MailDetail.as_view(), name='mail_detail'),
]