from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from homepage.models import Post, PostImage, Comment, Like
from users.models import Profile, Follower
from datetime import datetime
from django.contrib.auth.decorators import login_required
from homepage.forms import CommentForm, PostForm, ImageForm
from django.views.generic import DetailView, CreateView, ListView, UpdateView, DeleteView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db import transaction
from django.urls import reverse_lazy, reverse
from django.forms import modelformset_factory
from django.contrib import messages
from django.db.models import Q
# third- request looks for appropriate function to match and executes it (in this case it is an http response)


class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'homepage/home.html'
    ordering = ['-date_posted']
    context_object_name = 'posts'
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = datetime.now()
        context['followers'] = Follower.objects.filter(follower__username=self.request.user)
        context['likesbyuser'] = Like.objects.filter(liker=self.request.user)
        return context


def likePost(request):
    if request.method == 'GET':
        post_id = request.GET['post_id']
        likedpost = Post.objects.get(pk=post_id)  # getting the liked post

        if Like.objects.filter(post=likedpost, liker=request.user).exists():
            Like.objects.filter(post=likedpost, liker=request.user).delete()
        else:
            m = Like(post=likedpost, liker=request.user)  # creating like object
            m.save()  # saves into database
        return HttpResponse(likedpost.likes.count())
    else:
        return HttpResponse("Request method is not a GET")

def likeComment(request):
    if request.method == 'GET':
        comment_id = request.GET['comment_id']
        likedcomment = Comment.objects.get(pk=comment_id)  # getting the liked comment

        if Like.objects.filter(comment=likedcomment, liker=request.user).exists():
            Like.objects.filter(comment=likedcomment, liker=request.user).delete()
        else:
            m = Like(comment=likedcomment, liker=request.user)  # creating like object
            m.save()  # saves into database
        return HttpResponse(likedcomment.comment_likes.count())
    else:
        return HttpResponse("Request method is not a GET")


def search(request):
    form = SearchForm()
    return render(request, 'base.html', {'form': form})


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    context_object_name = 'p'


@login_required
def post(request):
    ImageFormSet = modelformset_factory(PostImage, fields=('modelimage',), labels={'modelimage': 'Image'}, extra=3, min_num=1)
    if request.method == 'POST':

        postForm = PostForm(request.POST)
        formset = ImageFormSet(request.POST, request.FILES, queryset=PostImage.objects.none())

        if postForm.is_valid() and formset.is_valid():
            post_form = postForm.save(commit=False)
            post_form.author = request.user
            post_form.save()

            for form in formset.cleaned_data:
                if form:
                    image = form['modelimage']
                    photo = PostImage(post=post_form, modelimage=image)
                    photo.save()
            messages.success(request, "Post Created!")
            return redirect('post-detail', pk=post_form.pk)
        else:
            messages.info(request, 'Please attach atleast one photo starting with the first photo box')

    else:
        postForm = PostForm()
        formset = ImageFormSet(queryset=PostImage.objects.none())
    return render(request, 'homepage/post_form.html', {'postForm': postForm, 'formset': formset})


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['caption']
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse('post-detail', kwargs={
            'pk': self.object.pk, })

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = Post.objects.get(pk=self.kwargs['pk'])  # ['pk'] is the pk assigned by to the comment button in the home.html. we are making the instance of the form assign the post field of the comment model to the Post object whos pk=self.kwargs['pk'] which is the storage location of url parameters
        return super().form_valid(form)
    

class ReplyCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        comment = Comment.objects.get(pk=self.kwargs['pk'])
        form.instance.parent = comment
        form.instance.post = comment.post
        return super().form_valid(form)
    
        

    

class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        comment = self.get_object()
        if self.request.user == comment.author:
            return True
        return False


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    success_url = '/'

    def test_func(self):
        comment = self.get_object()
        if self.request.user == comment.author:
            return True
        return False


class FollowerListView(LoginRequiredMixin, ListView):
    model = Follower

    def get_queryset(self):
        # org qs
        qs = super().get_queryset()
        # filter by var from captured url
        return qs.filter(Q(follower__username=self.kwargs['username']) | Q(being_followed__username=self.kwargs['username']))


class LikeListView(LoginRequiredMixin, ListView):
    model = Like

    def get_queryset(self):
        # org qs
        qs = super().get_queryset()
        # filter by var from captured url
        return qs.filter(post__pk=self.kwargs['pk'])

class CommentLikeListView(LoginRequiredMixin, ListView):
    model = Like

    def get_queryset(self):
        # org qs
        qs = super().get_queryset()
        # filter by var from captured url
        return qs.filter(comment__pk=self.kwargs['pk'])

def aboutUs(request):
    # displays http response for about us page
    response = render(request, 'homepage/aboutUs.html', {'title': 'About Us'})
    return response


def redirectAboutView(request):
    # redirects from /about to /about/us and displays http response of def aboutUs
    response = redirect('us/')
    return response


def aboutJobs(request):
    # displays http response for about jobs page
    response = HttpResponse('<h1>Caseygram About Jobs</h1>')
    return response


class ExploreListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'homepage/explore.html'
    ordering = ['-date_posted']
    context_object_name = 'posts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        followed_qs = Follower.objects.filter(follower=self.request.user)
        followed_users = []
        for i in followed_qs:
            followed_users.append(i.being_followed.username)
        context['followers'] = Follower.objects.filter(follower__username=self.request.user)

        context['profiles'] = Profile.objects.exclude(user=self.request.user).exclude(user__username__in=followed_users).order_by('-user__date_joined')[:4]

        followlist = []
        qs = Follower.objects.exclude(being_followed=self.request.user).filter(follower=self.request.user)
        for i in qs:
            followlist.append(i.being_followed.username)
        context['followlist'] = followlist

        return context


@login_required
def public_profile(request, username):  # learn how in bookmarks
    obj = User.objects.get(username=username)  # grabs <username> from url and stores it in obj to  be passed into the context
    context = {
        'posts': Post.objects.filter(author__username=obj).order_by('-date_posted'),
        'username': obj,  # obj is now accesible in the html via the variable {{ username }}
        'followers': Follower.objects.filter(being_followed=obj).exclude(follower=obj),
        'followees': Follower.objects.filter(follower=obj).exclude(being_followed=obj),
        'followcheck': Follower.objects.filter(follower=request.user, being_followed=obj),
    }
    response = render(request, 'homepage/public_profile.html', context, {'title': 'Public-Profile'})
    return response


class SearchListView(ListView):
    model = User
    template_name = 'auth/user_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q')
        context['query'] = self.request.GET.get('q')
        context['posts'] = Post.objects.filter(caption__icontains=query)
        return context

    def get_queryset(self):
        query = self.request.GET.get('q')
        object_list = User.objects.filter(username__icontains=query)
        return object_list


class LikeListView(LoginRequiredMixin, ListView):
    model = Like

    def get_queryset(self):
        # org qs
        qs = super().get_queryset()
        # filter by var from captured url
        return qs.filter(post__pk=self.kwargs['pk'])
