from django.contrib.auth.models import User
from django.db import models
from django.core.mail import send_mass_mail

from startup_test.settings import CURRENT_HOST, EMAIL_HOST_USER


class BlogPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    text = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def text_start(self):
        return ' '.join(self.text.split(' ')[:50])

    def save(self, *args, **kwargs):
        super(BlogPost, self).save(*args, **kwargs)
        subs_ids = Sub.objects.values_list('sub', flat=True).filter(author=self.user)
        emails = list(User.objects.values_list('email', flat=True).filter(id__in=subs_ids))
        subject = 'New Post in Your Feed!'
        link = '{}/post/{}'.format(CURRENT_HOST, self.id)
        message = 'Hi! You have a new post {} in your feed! Check it out: {}'.format(self.title, link)
        from_email = EMAIL_HOST_USER
        send_mass_mail(((subject, message, from_email, emails),), fail_silently=False)


class Sub(models.Model):
    sub = models.ForeignKey(User, related_name='sub', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='author', on_delete=models.CASCADE)

    def __str__(self):
        return '{} is subscribed to {}'.format(self.sub.username, self.author.username)


class ReadPost(models.Model):
    user = models.ForeignKey(User)
    post = models.ForeignKey(BlogPost)
