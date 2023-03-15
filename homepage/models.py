from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image
from notifications.signals import notify
from django.utils.text import Truncator

# models from my understanding are the location of all the info about your data. you use it to make databases


class Post(models.Model):
    caption = models.CharField(max_length=2200, blank=True)  # caption is a field in this Post model. it specifies a class attribute Charfield and represents a database column. blank=True lets the field be optional left empty
    date_posted = models.DateTimeField(default=timezone.now)  # instead of hard setting the time this timezone.now takes the users timezone into consideration.
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # foreign key calls on an outside model whether imported or in this file, CASCADE will delete the post if
    # the User is deleted but wont delete the user if the post if deleted
    # likes?
    # picture = models.

    def __str__(self):
        return self.caption


class PostImage(models.Model):
    post = models.ForeignKey(Post, related_name='images', on_delete=models.CASCADE)
    modelimage = models.ImageField(upload_to='post_images')


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE, null=True)
    content = models.CharField(max_length=500, blank=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(default=timezone.now)
    parent = models.ForeignKey('self', null=True, on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return self.content             

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.post.pk})  # returns a string to the post detail that uses the pk of the comment instance. post. pk to link to the correct detail page ie. /post/

    def save(self, *args, **kwargs):
        super(Comment, self).save(*args, **kwargs)
        n = 4
        truncatewords = Truncator(self.content).words(n)
        notify.send(self.author, recipient=self.post.author, verb='commented "' + truncatewords + '" on your post!', action_object=self.post, description='comment', target=self)


class Like(models.Model):
    liker = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes', null= True)
    date_created = models.DateTimeField(default=timezone.now)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='comment_likes', null=True)

    def save(self, *args, **kwargs):
        super(Like, self).save(*args, **kwargs)
        if self.post:
            notify.send(self.liker, recipient=self.post.author, verb='liked your post!', action_object=self.post, description='like', target=self)
        elif self.comment:
            notify.send(self.liker, recipient=self.comment.author, verb='liked your comment!', action_object=self.comment, description='like', target=self)
    
    def __str__(self):
        return f'{self.liker} {self.comment}' 
            
# this model is many to one (many images for one user) related to the Post model. the equilavalcy to match users is:
# PostImage.objects.get(pk=1).post =  Post.objects.get(pk=4)
