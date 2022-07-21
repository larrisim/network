from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='liked_user', blank=True, null = True)
    created_at = models.TextField(blank=True, null=True)
    updated_at = models.TextField(blank=True, null=True)


    def __str__(self):
        return f"{self.author} posted {self.content}"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.TextField(blank=True, null=True)
    updated_at = models.TextField(blank=True, null=True)
    #created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.commenter} commented {self.comment} at {self.post}"

class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    follower = models.ManyToManyField(User, blank=True, related_name='followed_user')
    following = models.ManyToManyField(User, blank=True, related_name='following_user')

    def __str__(self):
        return f"{self.user}"
