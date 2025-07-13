from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from .forms import LoginForm, RegisterForm
from .models import Message,Post, Profile, Comment, Like, Follow, Notification

def home(request):
    if request.user.is_authenticated:
        return redirect('feed')
    return render(request, 'base.html')

@login_required
def view_profile(request):
    profile = request.user.profile
    posts = Post.objects.filter(user=request.user).order_by('-created_at')
    post_count = posts.count()
    return render(request, 'profile.html', {
        'profile': profile,
        'posts': posts,
        'post_count': post_count,
    })

@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == 'POST':
        profile.bio = request.POST.get('bio')
        profile.sport = request.POST.get('sport')
        profile.position = request.POST.get('position')
        profile.level = request.POST.get('level')
        profile.experience = request.POST.get('experience')
        profile.school = request.POST.get('school')
        profile.grad_year = request.POST.get('grad_year')

        if 'profile_image' in request.FILES:
            profile.profile_image = request.FILES['profile_image']
        if 'cover_image' in request.FILES:
            profile.cover_image = request.FILES['cover_image']

        profile.save()
        return redirect('view_profile')

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

@csrf_exempt
@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image')
        video = request.FILES.get('video')

        Post.objects.create(
            user=request.user,
            content=content,
            image=image,
            video=video
        )
        return redirect('feed')

@login_required
def feed(request):
    following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    posts = Post.objects.filter(
    models.Q(user_id__in=following_ids) | models.Q(user=request.user)
).order_by('-created_at')

    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get liked posts by current user
    liked_post_ids = Like.objects.filter(user=request.user, post__in=page_obj).values_list('post_id', flat=True)

    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = None

    return render(request, 'feed.html', {
        'posts': page_obj,
        'profile': profile,
        'page_obj': page_obj,
        'liked_post_ids': liked_post_ids
    })

def login_view(request):
    form = LoginForm(request.POST or None)
    error = None

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
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
            Profile.objects.create(
                user=user,
                role=form.cleaned_data['role'],
                school=form.cleaned_data['school'],
                grad_year=form.cleaned_data['grad_year'],
                profile_image=request.FILES.get('profile_image')
            )
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
    users = User.objects.exclude(id=request.user.id)
    messages = Message.objects.filter(Q(sender=request.user) | Q(recipient=request.user))
    return render(request, 'inbox.html', {'users': users, 'messages': messages})


@login_required
def chat_view(request, username):
    other_user = get_object_or_404(User, username=username)
    messages = Message.objects.filter(
        Q(sender=request.user, recipient=other_user) |
        Q(sender=other_user, recipient=request.user)
    ).order_by('timestamp')

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(sender=request.user, recipient=other_user, content=content)
            return redirect('chat', username=username)

    return render(request, 'chat.html', {
        'other_user': other_user,
        'messages': messages
    })
