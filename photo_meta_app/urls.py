from django.urls import path
from . import views

app_name = 'photo_meta_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add_metadata, name='add_metadata'),
    path('upload/', views.upload_file, name='upload_file'),
    path('view/<str:filename>/', views.view_file, name='view_file'),
]
