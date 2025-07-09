# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_posts, name='view_posts'),
    path('sync/', views.sync_more_posts, name='sync_more_posts'),
    path('edit/<int:post_id>/', views.edit_post, name='edit_post'),
    path('delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path('post/<int:post_id>/', views.view_single_post, name='view_single_post'),
]