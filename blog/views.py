from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic import DetailView
from django.views.generic import ListView

from blog.forms import LoginForm
from blog.models import BlogPost, Sub, ReadPost


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect('/my_blog')
            return render(request, 'blog/login.html', {'form': form, 'error': 'Wrong username or password'})
    else:
        form = LoginForm()
    return render(request, 'blog/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/login')


class MyBlog(LoginRequiredMixin, ListView):
    model = BlogPost
    template_name = 'blog/my_blog.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return BlogPost.objects.filter(user=self.request.user).order_by('-date_created')

    def get_context_data(self, **kwargs):
        context = super(MyBlog, self).get_context_data(**kwargs)
        read_list = list(ReadPost.objects.values_list('post', flat=True).filter(user=self.request.user))
        context['read_list'] = read_list
        return context


class AllPosts(LoginRequiredMixin, ListView):
    model = BlogPost
    template_name = 'blog/all_posts.html'
    context_object_name = 'posts'
    queryset = BlogPost.objects.order_by('-date_created')

    def get_context_data(self, **kwargs):
        context = super(AllPosts, self).get_context_data(**kwargs)
        read_list = list(ReadPost.objects.values_list('post', flat=True).filter(user=self.request.user))
        context['read_list'] = read_list
        context['current_user'] = self.request.user
        return context


class Subscriptions(LoginRequiredMixin, ListView):
    model = BlogPost
    template_name = 'blog/subscriptions.html'
    context_object_name = 'posts'

    def get_queryset(self):
        authors = Sub.objects.values_list('author', flat=True).filter(sub=self.request.user)
        return BlogPost.objects.exclude(user=self.request.user).filter(user__in=authors).order_by('-date_created')

    def get_context_data(self, **kwargs):
        context = super(Subscriptions, self).get_context_data(**kwargs)
        read_list = list(ReadPost.objects.values_list('post', flat=True).filter(user=self.request.user))
        context['read_list'] = read_list
        return context


class PostDetails(LoginRequiredMixin, DetailView):
    model = BlogPost
    context_object_name = 'post'
    template_name = 'blog/post_details.html'

    def get_context_data(self, **kwargs):
        context = super(PostDetails, self).get_context_data(**kwargs)
        read_list = list(ReadPost.objects.values_list('post', flat=True).filter(user=self.request.user))
        context['read_list'] = read_list
        subscriptions = list(Sub.objects.values_list('author', flat=True).filter(sub=self.request.user))
        context['subscriptions'] = subscriptions
        context['current_user'] = self.request.user
        return context


class CreatePost(LoginRequiredMixin, View):
    @staticmethod
    def get(request):
        return render(request, 'blog/create_post.html')

    @staticmethod
    def post(request):
        title = request.POST.get('title', None)
        text = request.POST.get('text', None)
        if not title or not text:
            return render(request, 'blog/create_post.html', {'error': 'Please fill out everything'})
        else:
            user = request.user
            BlogPost.objects.create(user=user, title=title, text=text)
            return HttpResponseRedirect('/my_blog')


class MarkAsRead(LoginRequiredMixin, View):
    def post(self, request):
        post_id = request.POST['mark_as_read']
        ReadPost.objects.create(user=self.request.user, post=BlogPost.objects.get(id=post_id))
        return HttpResponseRedirect('/post/' + post_id)


class Subscribe(LoginRequiredMixin, View):
    def post(self, request):
        Sub.objects.create(sub=self.request.user, author=User.objects.get(username=request.POST['subscribe']))
        return HttpResponseRedirect('/post/' + request.POST['post_id'])


class Unsubscribe(LoginRequiredMixin, View):
    def post(self, request):
        Sub.objects.filter(sub=self.request.user,
                           author=User.objects.get(username=request.POST['unsubscribe'])).delete()
        return HttpResponseRedirect('/post/' + request.POST['post_id'])
