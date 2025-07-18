from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    ROLE_CHOICES = [
        ('athlete', 'Athlete'),
        ('sponsor', 'Sponsor'),
        ('fan', 'Fan'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    school = models.CharField(max_length=100, blank=True)
    grad_year = models.IntegerField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', default='profile_images/default.png', blank=True)
    cover_image = models.ImageField(upload_to='profile_images/covers/', default='profile_images/covers/default.jpg', blank=True)
    bio = models.TextField(blank=True)

    sport = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    level = models.CharField(max_length=100, blank=True)
    experience = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
    
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    video = models.FileField(upload_to='post_videos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:50]
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    content = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.sender} to {self.recipient}"

class Event(models.Model):
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    title = models.CharField(max_length=200)
    description = models.TextField()
    photo = models.ImageField(upload_to='event_photos/', blank=True, null=True)
    event_date = models.DateTimeField()
    venue_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    def get_attending_count(self):
        return self.event_responses.filter(response_type='attending').count()
    
    def get_interested_count(self):
        return self.event_responses.filter(response_type='interested').count()

class EventResponse(models.Model):
    RESPONSE_CHOICES = [
        ('interested', 'Interested'),
        ('attending', 'Attending'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_responses')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_responses')
    response_type = models.CharField(max_length=20, choices=RESPONSE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['event', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.response_type} - {self.event.title}"