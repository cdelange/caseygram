import datetime
from homepage.models import Comment, Post
from django.contrib.auth.models import User
from django.test import TestCase

class CommentTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username= "testuser", password= "testuser")
        # self.profile= Profile.objects.create(user= self.user)
        
        self.post = Post.objects.create(caption= "hello world", author= self.user)

        self.comment = Comment.objects.create(post= self.post, content= "how are you", author= self.user)

    def test_comment_create(self):
        comment = Comment.objects.get(post=self.post)
        self.assertEqual(comment.content, "how are you")