from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('feed/', views.feed, name='feed'),
    path('post/', views.create_post, name='create_post'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.view_profile, name='profile'),  # actual profile page
    path('profile/edit/', views.edit_profile, name='edit_profile'),  # for editing
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('comment/<int:post_id>/', views.comment_post, name='comment_post'),
    path('notifications/', views.notifications, name='notifications'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('inbox/', views.inbox, name='inbox'),
    path('chat/<str:username>/', views.chat_view, name='chat'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
