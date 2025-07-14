from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from .forms import LoginForm, RegisterForm
from .models import Message,Post, Profile, Comment, Like, Follow, Notification, Event, EventResponse
from django.utils import timezone
from django.http import JsonResponse

def home(request):
    if request.user.is_authenticated:
        return redirect('feed')
    return render(request, 'base.html')

@login_required
def view_profile(request):
    profile = request.user.profile
    posts = Post.objects.filter(user=request.user).order_by('-created_at')
    post_count = posts.count()
    followers_count = Follow.objects.filter(following=request.user).count()
    following_count = Follow.objects.filter(follower=request.user).count()
    
    # Get events if user is a sponsor
    events = []
    if profile.role == 'sponsor':
        events = Event.objects.filter(organizer=request.user).order_by('-created_at')
    
    return render(request, 'profile.html', {
        'profile': profile,
        'posts': posts,
        'events': events,
        'post_count': post_count,
        'followers_count': followers_count,
        'following_count': following_count,
    })

@login_required
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.profile
    posts = Post.objects.filter(user=user).order_by('-created_at')
    post_count = posts.count()
    
    # Check if current user is following this user
    is_following = Follow.objects.filter(follower=request.user, following=user).exists()
    
    # Get follower and following counts
    followers_count = Follow.objects.filter(following=user).count()
    following_count = Follow.objects.filter(follower=user).count()
    
    return render(request, 'user_profile.html', {
        'profile_user': user,
        'profile': profile,
        'posts': posts,
        'post_count': post_count,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count,
    })

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    
    # Don't allow following yourself
    if user_to_follow == request.user:
        return redirect('user_profile', username=username)
    
    # Check if already following
    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )
    
    if not created:
        # If already following, unfollow
        follow.delete()
        action = 'unfollowed'
    else:
        # If not following, follow
        action = 'followed'
        # Create notification
        Notification.objects.create(
            user=user_to_follow,
            content=f"{request.user.username} started following you"
        )
    
    return redirect('user_profile', username=username)

@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == 'POST':
        profile.bio = request.POST.get('bio', '')
        profile.sport = request.POST.get('sport', '')
        profile.position = request.POST.get('position', '')
        profile.level = request.POST.get('level', '')
        
        # Handle experience field - convert empty string to None
        experience_value = request.POST.get('experience', '')
        if experience_value == '':
            profile.experience = None
        else:
            try:
                profile.experience = int(experience_value)
            except ValueError:
                profile.experience = None
        
        profile.school = request.POST.get('school', '')
        
        # Handle grad_year field - convert empty string to None
        grad_year_value = request.POST.get('grad_year', '')
        if grad_year_value == '':
            profile.grad_year = None
        else:
            try:
                profile.grad_year = int(grad_year_value)
            except ValueError:
                profile.grad_year = None

        if 'profile_image' in request.FILES:
            profile.profile_image = request.FILES['profile_image']
        if 'cover_image' in request.FILES:
            profile.cover_image = request.FILES['cover_image']

        profile.save()
        return redirect('profile')

    return render(request, 'edit_profile.html', {'profile': profile})

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
    else:
        Notification.objects.create(user=post.user, content=f"{request.user.username} liked your post")
    return redirect('feed')

@login_required
def comment_post(request, post_id):
    if request.method == 'POST':
        content = request.POST.get('comment')
        post = get_object_or_404(Post, id=post_id)
        Comment.objects.create(post=post, user=request.user, content=content)
        Notification.objects.create(user=post.user, content=f"{request.user.username} commented on your post")
    return redirect('feed')

@login_required
def notifications(request):
    notes = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notes})

@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image')
        video = request.FILES.get('video')

        if not content.strip():
            return render(request, 'create_post.html', {
                'error': 'Post content is required.',
                'form': {'content': {'value': content}}
            })

        Post.objects.create(
            user=request.user,
            content=content,
            image=image,
            video=video
        )
        return redirect('feed')
    
    return render(request, 'create_post.html')

@login_required
def feed(request):
    # Show all posts and events, ordered by creation date
    posts = Post.objects.all().order_by('-created_at')
    events = Event.objects.all().order_by('-created_at')
    
    # Combine posts and events and sort by creation date
    from itertools import chain
    from operator import attrgetter
    
    all_items = sorted(
        chain(posts, events),
        key=attrgetter('created_at'),
        reverse=True
    )

    # Pagination
    paginator = Paginator(all_items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get liked posts by current user
    post_items = [item for item in page_obj if hasattr(item, 'user') and hasattr(item, 'likes')]
    liked_post_ids = Like.objects.filter(user=request.user, post__in=post_items).values_list('post_id', flat=True)

    # Get user responses to events
    event_items = [item for item in page_obj if hasattr(item, 'organizer')]
    user_event_responses = {}
    if event_items:
        responses = EventResponse.objects.filter(user=request.user, event__in=event_items)
        for response in responses:
            user_event_responses[response.event.id] = response.response_type

    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = None

    return render(request, 'feed.html', {
        'items': page_obj,
        'profile': profile,
        'page_obj': page_obj,
        'liked_post_ids': liked_post_ids,
        'user_event_responses': user_event_responses
    })

def login_view(request):
    form = LoginForm(request.POST or None)
    error = None

    if request.method == 'POST':
        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Try to authenticate with username first
            user = authenticate(request, username=username_or_email, password=password)
            
            # If that fails, try to find user by email and authenticate
            if user is None:
                try:
                    # Use filter().first() instead of get() to handle multiple users with same email
                    user_obj = User.objects.filter(email=username_or_email).first()
                    if user_obj:
                        user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None
            
            if user:
                login(request, user)
                return redirect('feed')
            else:
                error = "Invalid credentials."

    return render(request, 'login.html', {'form': form, 'error': error})

def logout_view(request):
    logout(request)
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # Handle profile image if uploaded
            if request.FILES.get('profile_image'):
                profile = user.profile
                profile.profile_image = request.FILES.get('profile_image')
                profile.save()
            login(request, user)
            return redirect('feed')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    if request.method == 'POST':
        post.content = request.POST.get('content')
        if 'image' in request.FILES:
            post.image = request.FILES['image']
        post.save()
        return redirect('feed')
    return render(request, 'edit_post.html', {'post': post})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    if request.method == 'POST':
        post.delete()
        return redirect('feed')
    return render(request, 'confirm_delete.html', {'post': post})

@login_required
def inbox(request):
    # Get all users except current user
    users = User.objects.exclude(id=request.user.id).prefetch_related('profile')
    
    # Get the selected user from query parameter
    selected_user = request.GET.get('user')
    other_user = None
    messages = []
    
    if selected_user:
        try:
            other_user = User.objects.get(username=selected_user)
            # Get messages between current user and selected user
            messages = Message.objects.filter(
                Q(sender=request.user, recipient=other_user) |
                Q(sender=other_user, recipient=request.user)
            ).order_by('timestamp')
            
            # Mark messages from other user as read
            Message.objects.filter(
                sender=other_user, 
                recipient=request.user, 
                is_read=False
            ).update(is_read=True)
        except User.DoesNotExist:
            pass
    
    # Handle message sending
    if request.method == 'POST' and other_user:
        content = request.POST.get('content')
        if content and content.strip():
            Message.objects.create(
                sender=request.user, 
                recipient=other_user, 
                content=content.strip()
            )
            # Redirect to same page to avoid form resubmission
            return redirect(f'/inbox/?user={other_user.username}')
    
    # Get last message for each conversation and create user list
    user_conversations = {}
    for user in users:
        last_message = Message.objects.filter(
            Q(sender=request.user, recipient=user) |
            Q(sender=user, recipient=request.user)
        ).order_by('-timestamp').first()
        
        user_conversations[user] = {
            'user': user,
            'last_message': last_message,
            'unread_count': Message.objects.filter(
                sender=user, 
                recipient=request.user, 
                is_read=False
            ).count() if hasattr(Message, 'is_read') else 0
        }
    
    # Sort users: those with conversations first (by recent message), then others alphabetically
    conversations = []
    users_without_conversations = []
    
    for user, conv_data in user_conversations.items():
        if conv_data['last_message']:
            conversations.append(conv_data)
        else:
            users_without_conversations.append({
                'user': user,
                'last_message': None,
                'unread_count': 0
            })
    
    # Sort conversations by last message timestamp (most recent first)
    conversations.sort(key=lambda x: x['last_message'].timestamp if x['last_message'] else timezone.now(), reverse=True)
    
    # Sort users without conversations alphabetically by name
    users_without_conversations.sort(key=lambda x: x['user'].get_full_name() or x['user'].username)
    
    # Combine both lists
    all_conversations = conversations + users_without_conversations
    

    
    return render(request, 'inbox.html', {
        'conversations': all_conversations,
        'other_user': other_user,
        'messages': messages,
        'selected_user': selected_user
    })


@login_required
def chat_view(request, username):
    other_user = get_object_or_404(User, username=username)
    messages = Message.objects.filter(
        Q(sender=request.user, recipient=other_user) |
        Q(sender=other_user, recipient=request.user)
    ).order_by('timestamp')

    # Mark messages from other user as read
    Message.objects.filter(
        sender=other_user, 
        recipient=request.user, 
        is_read=False
    ).update(is_read=True)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(sender=request.user, recipient=other_user, content=content)
            return redirect('chat', username=username)

    return render(request, 'chat.html', {
        'other_user': other_user,
        'messages': messages
    })

@login_required
def current_user_followers(request):
    """Get followers for the current logged-in user"""
    followers = Follow.objects.filter(following=request.user).select_related('follower__profile')
    followers_data = []
    for f in followers:
        follower = f.follower
        profile = getattr(follower, 'profile', None)
        followers_data.append({
            'username': follower.username,
            'full_name': follower.get_full_name(),
            'profile_image': profile.profile_image.url if profile and profile.profile_image else '/media/profile_images/default.png',
        })
    return JsonResponse({'followers': followers_data})

@login_required
def current_user_following(request):
    """Get following list for the current logged-in user"""
    following = Follow.objects.filter(follower=request.user).select_related('following__profile')
    following_data = []
    for f in following:
        following_user = f.following
        profile = getattr(following_user, 'profile', None)
        following_data.append({
            'username': following_user.username,
            'full_name': following_user.get_full_name(),
            'profile_image': profile.profile_image.url if profile and profile.profile_image else '/media/profile_images/default.png',
        })
    return JsonResponse({'following': following_data})

@login_required
def user_followers(request, username):
    user = get_object_or_404(User, username=username)
    followers = Follow.objects.filter(following=user).select_related('follower__profile')
    followers_data = []
    for f in followers:
        follower = f.follower
        profile = getattr(follower, 'profile', None)
        followers_data.append({
            'username': follower.username,
            'full_name': follower.get_full_name(),
            'profile_image': profile.profile_image.url if profile and profile.profile_image else '/media/profile_images/default.png',
        })
    return JsonResponse({'followers': followers_data})

@login_required
def user_following(request, username):
    user = get_object_or_404(User, username=username)
    following = Follow.objects.filter(follower=user).select_related('following__profile')
    following_data = []
    for f in following:
        following_user = f.following
        profile = getattr(following_user, 'profile', None)
        following_data.append({
            'username': following_user.username,
            'full_name': following_user.get_full_name(),
            'profile_image': profile.profile_image.url if profile and profile.profile_image else '/media/profile_images/default.png',
        })
    return JsonResponse({'following': following_data})

# Event Views
@login_required
def create_event(request):
    # Check if user is a sponsor
    if request.user.profile.role != 'sponsor':
        return redirect('feed')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        event_date = request.POST.get('event_date')
        venue_name = request.POST.get('venue_name')
        photo = request.FILES.get('photo')
        
        if title and description and event_date and venue_name:
            event = Event.objects.create(
                organizer=request.user,
                title=title,
                description=description,
                event_date=event_date,
                venue_name=venue_name,
                photo=photo
            )
            return redirect('event_detail', event_id=event.id)
    
    return render(request, 'create_event.html')

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    user_response = None
    if request.user.is_authenticated:
        user_response = EventResponse.objects.filter(event=event, user=request.user).first()
    
    return render(request, 'event_detail.html', {
        'event': event,
        'user_response': user_response,
        'is_organizer': event.organizer == request.user
    })

@login_required
def respond_to_event(request, event_id):
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        response_type = request.POST.get('response_type')
        
        if response_type in ['interested', 'attending']:
            # Remove existing response if any
            EventResponse.objects.filter(event=event, user=request.user).delete()
            
            # Create new response
            EventResponse.objects.create(
                event=event,
                user=request.user,
                response_type=response_type
            )
            
            # Create notification for organizer
            Notification.objects.create(
                user=event.organizer,
                content=f"{request.user.username} is {response_type} in your event '{event.title}'"
            )
    
    return redirect('event_detail', event_id=event_id)

@login_required
def event_responses(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # Check if user is the organizer
    if event.organizer != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    attending_users = EventResponse.objects.filter(
        event=event, 
        response_type='attending'
    ).select_related('user__profile')
    
    interested_users = EventResponse.objects.filter(
        event=event, 
        response_type='interested'
    ).select_related('user__profile')
    
    attending_data = []
    for response in attending_users:
        profile = getattr(response.user, 'profile', None)
        attending_data.append({
            'username': response.user.username,
            'full_name': response.user.get_full_name(),
            'profile_image': profile.profile_image.url if profile and profile.profile_image else '/media/profile_images/default.png',
        })
    
    interested_data = []
    for response in interested_users:
        profile = getattr(response.user, 'profile', None)
        interested_data.append({
            'username': response.user.username,
            'full_name': response.user.get_full_name(),
            'profile_image': profile.profile_image.url if profile and profile.profile_image else '/media/profile_images/default.png',
        })
    
    return JsonResponse({
        'attending': attending_data,
        'interested': interested_data
    })
