from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from homepage.forms import CommentForm


class TestViews(TestCase):
    # def setUp(self):
    #     self.user = User.objects.create_user(username= "user", password= "password")
        # self.profile= Profile.objects.create(user= self.user)


    def test_view_deny_anonymous(self):
        url = reverse('public-profile', kwargs={'username':'username'})
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, '/login/')
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, '/login/')

    def test_call_view_load(self):
        self.client.login(username='user', password='password')  
        url = reverse('public-profile', kwargs={'username':self.user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'homepage/public_profile.html')
    
    def test_form_content(self):
        form = CommentForm(data={"content": "testing comment"})

        self.assertTrue(form.is_valid())
        