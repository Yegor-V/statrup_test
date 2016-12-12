from django.conf.urls import url
from django.contrib import admin
from blog.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'login/?$', user_login, name='login'),
    url(r'^logout/?$', user_logout, name='logout'),

    url(r'^my_blog/?$', MyBlog.as_view(), name='my-blog'),
    url(r'^all_posts$', AllPosts.as_view(), name='all-posts'),
    url(r'^$', Subscriptions.as_view(), name='subscriptions'),

    url(r'^post/(?P<pk>[0-9]+)/?$', PostDetails.as_view(), name='post-details'),

    url(r'^create_post/?$', CreatePost.as_view(), name='create-post'),

    url(r'^mark_as_read/?$', MarkAsRead.as_view(), name='mark-as-read'),

    url(r'^subscribe/?$', Subscribe.as_view(), name='subscribe'),
    url(r'^unsubscribe/?$', Unsubscribe.as_view(), name='unsubscribe'),
]
