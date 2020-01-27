from django.db import models
from users.models import User
# Create your models here.


class Post(models.Model):
    title = models.CharField(max_length=50)
    text = models.TextField(default="")
    likes = models.ManyToManyField(User, related_name="favorite_posts")


class Attach(models.Model):
    file_url = models.FileField(upload_to="posts_attachments")
    file_extension = models.CharField(max_length=10)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)