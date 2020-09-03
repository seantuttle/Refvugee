from django.urls import reverse
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.mail import send_mail
from Refvugee import settings
from users.models import Profile

class Post(models.Model):
    title = models.CharField(max_length=100)
    keywords = models.CharField(default='', max_length=100)
    about = models.TextField(default='', max_length=200)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        self.date_posted = timezone.now()

        users_to_notify_queryset = Profile.objects.filter(notify=True)

        for user_prof in users_to_notify_queryset:
            user_to_notify = [user_prof.user.email]
            self.send_post_notification_email(user_to_notify)

        super().save(*args, *kwargs)

    def send_post_notification_email(self, recipient):
        subject = 'New Refvugee Post!'
        message = None
        from_email = settings.EMAIL_HOST_USER
        author = User.objects.get(id=self.author_id)

        # TODO - make this message look really good since it actual gets emailed to our visitors
        html_message_base = f"""
                        <head>
                            <style>
                                h2, h3 {{ color: red; }}
                                h4 {{ color: rgb(173, 123, 0); }}
                                span {{ color: black; }}
                            </style>
                        </head>
                        <body>
                            <h2>REFVUGEE POST NOTIFICATION</h2>
                            <h4>Post Title: <span>{self.title}</span></h4>
                            <h4>Post Author: <span>{author}</span></h4>
                            <h4>About the Post: <span>{self.about}</span></h4>
                            <h4>Post Content: </h4>
                            <hr>    
                            <p>{self.content}</p>
                            <hr>
                            <br>
                            <h3>--Automated from Refvugee</h3>
                        </body>
                        """

        html_message_test = None

        send_mail(subject, message, from_email, recipient, html_message=html_message_base)


class Comment(models.Model):
    title = models.CharField(null=True, max_length=100)
    content = models.TextField(max_length=2000)
    date_posted = models.DateTimeField(default=timezone.now)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.post.pk})

# It breaks if I delete this method for some reason
def create_deleted_comment():
    return None

class Reply(models.Model):
    title = models.CharField(null=True, max_length=100)
    content = models.TextField(max_length=2000)
    date_posted = models.DateTimeField(default=timezone.now)
    parent_comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE)


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.super_comment.post.pk})
    
