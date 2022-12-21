from django.urls import path, include
from . import views
from .views import PostDetailView, CommentCreateView, ReplyCreateView, public_profile, CommentUpdateView, CommentDeleteView, FollowerListView, PostDeleteView, PostUpdateView, likePost, SearchListView, PostListView, ExploreListView
import notifications.urls


# second- truncated request is sent here and a match is searched for in url patterns again
urlpatterns = [
    path('', PostListView.as_view(), name='caseygram-home'),
    path('about/us/', views.aboutUs, name='caseygram-about-us'),
    path('about/jobs/', views.aboutJobs, name='caseygram-about-jobs'),
    path('about/', views.redirectAboutView, name='caseygram-about-us-redirect'),
    path('explore/', ExploreListView.as_view(), name='caseygram-explore'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('comment/<int:pk>/update/', CommentUpdateView.as_view(), name='comment-update'),
    path('comment/<int:pk>/reply/', ReplyCreateView.as_view(), name='comment-reply'),
    path('comment/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment-delete'),
    path('comment/<int:pk>/', CommentCreateView.as_view(), name='comment-form'),
    path('profile/<str:username>/', views.public_profile, name='public-profile'),
    path('post/new/', views.post, name='post-add'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('profile/<str:username>/followers/', views.
         FollowerListView.as_view(), name='follower-list'),
    path('profile/<str:username>/following/', views.
         FollowerListView.as_view(), name='following-list'),
    path('post/<int:pk>/likes/', views.LikeListView.as_view(), name='likes-list'),
    path('post/<int:pk>/commentlikes/', views.CommentLikeListView.as_view(), name='comment-likes-list'),
    path('search/', views.SearchListView.as_view(), name="search-list"),
    path('likepost/', views.likePost, name='likepost'),
    path('likecomment/', views.likeComment, name='likecomment'),
    path('inbox/notifications/', include(notifications.urls, namespace='notifications')),
]
