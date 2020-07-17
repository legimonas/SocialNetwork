from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from users.models import User
from django.utils import timezone
# Create your models here.


class Post(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=50)
    text = models.TextField(default="")
    publication_date = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(User, related_name="favorite_posts")


class Attach(models.Model):
    file = models.FileField(upload_to="posts_attachments")
    file_extension = models.CharField(max_length=10)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)