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
    path('profile/followers/', views.current_user_followers, name='current_user_followers'),  # AJAX followers list for current user
    path('profile/following/', views.current_user_following, name='current_user_following'),  # AJAX following list for current user
    path('profile/<str:username>/', views.user_profile, name='user_profile'),  # other user's profile
    path('profile/edit/', views.edit_profile, name='edit_profile'),  # for editing
    path('profile/<str:username>/followers/', views.user_followers, name='user_followers'),  # AJAX followers list
    path('profile/<str:username>/following/', views.user_following, name='user_following'),  # AJAX following list
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('comment/<int:post_id>/', views.comment_post, name='comment_post'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('notifications/', views.notifications, name='notifications'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('inbox/', views.inbox, name='inbox'),
    path('chat/<str:username>/', views.chat_view, name='chat'),
    path('event/create/', views.create_event, name='create_event'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('event/<int:event_id>/respond/', views.respond_to_event, name='respond_to_event'),
    path('event/<int:event_id>/responses/', views.event_responses, name='event_responses'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
