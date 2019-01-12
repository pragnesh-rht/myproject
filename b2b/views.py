from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from rest_framework import viewsets, permissions, mixins

from b2b.permissions import IsAuthorOrReadOnly
from users.models import Profile
from .forms import PostForm, BidForm, PostUpdateForm, ImageFormSet
from .models import Post, Images, Bidder
from .serializers import PostSerializer, ImagesSerializer, BidderSerializer, ProfileSerializer


class ProfileView(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class PostView(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ImagesView(viewsets.ModelViewSet):
    queryset = Images.objects.all()
    serializer_class = ImagesSerializer


class BidderView(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Bidder.objects.all()
    serializer_class = BidderSerializer

    def perform_create(self, serializer):
        serializer.save(bid_author=self.request.user)


##################
# API VIEW ENDED #
##################


class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'b2b/adCreate.html'
    success_url = 'b2b/home.html'

    def get_context_data(self, **kwargs):
        context = super(PostCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['postImages'] = ImageFormSet(self.request.POST, self.request.FILES,
                                                 queryset=Images.objects.none())
        else:
            context['postImages'] = ImageFormSet(queryset=Images.objects.none())
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['postImages']
        if form.is_valid() and formset.is_valid():
            post_form = form.save(commit=False)
            post_form.author = self.request.user
            post_form.save()

            for imageform in formset.cleaned_data:
                if imageform:
                    image = imageform['post_image']
                    photo = Images(post=post_form, post_image=image)
                    photo.save()
            obj = Images.objects.filter(post_id=post_form.pk)
            if not obj.exists():
                image = 'default_post_image.jpg'
                photo = Images(post=post_form, post_image=image)
                photo.save()

            messages.success(self.request, "Your post has been created successfully")
            return HttpResponseRedirect("/")
        else:
            print(form.errors, formset.errors)


class PostListView(ListView):
    model = Post
    template_name = 'b2b/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 8


class UserPostListView(ListView):
    model = Post
    template_name = 'b2b/user_posts.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 8

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post


class BidUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = BidForm
    template_name = 'b2b/post_detail.html'

    def form_valid(self, form):
        context = self.get_context_data()
        object = context['post']
        if form.is_valid():
            if object.author is not self.request.user:
                bidder = Bidder(post=object, prices=form.instance.current_price, bid_author=self.request.user)
                bidder.save()
                messages.success(self.request, "Your Bid has been Submitted Successfully!")
                return super().form_valid(form)
            else:
                messages.info(self.request, "You can not bid on your own post.")
                return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        obj = self.get_object()
        bidderQS = Bidder.objects.filter(post_id=obj)
        data['bidderQS'] = bidderQS
        return data


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostUpdateForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post_obj = self.get_object()
        if self.request.user == post_obj.author:
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


def about(request):
    return render(request, 'b2b/about.html', {'title': 'About'})
