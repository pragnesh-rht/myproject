from django.urls import path, include

from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('post', views.PostView)
router.register('images', views.ImagesView)
router.register('bidder', views.BidderView)
router.register('profile', views.ProfileView)

urlpatterns = [
    path('api/', include(router.urls)),

    path('', views.PostListView.as_view(), name='b2b-home'),

    path('user/<str:username>', views.UserPostListView.as_view(), name='user-post'),
    # path('post/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('post/new/', views.PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', views.PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:pk>/bidUpdate', views.BidUpdateView.as_view(), name='bid-update'),

    path('about/', views.about, name='b2b-about'),
]

# path('', views.home, name='b2b-home'),
