from django import forms
from django.core.mail import send_mail
from django.contrib.auth.models import User
from Refvugee import settings
from .models import Comment

class CommentForm(forms.ModelForm):
    title = forms.CharField(max_length=100)
    content = forms.CharField(label='Comment', widget=forms.Textarea(attrs={'rows': 10, 'cols': 40}))
    post = forms.HiddenInput()

    class Meta:
        model = Comment
        fields = ['title', 'content']

class ReportForm(forms.Form):
    subject = forms.CharField(max_length=50)
    complaint = forms.CharField(widget=forms.Textarea(attrs={'rows': 10, 'cols': 40}))

    def send_report_email(self, subject, complaint, reporter, reportee, post, comment, review, delete, parent_comment=None):
        message = None
        email_subject = 'Refvugee Comment Report Form'
        replying_to_html_string = ''
        if parent_comment:
            replying_to_html_string = f'<h4>Replying To: <span>"{parent_comment.title}" by {parent_comment.author}</span></h4>'

        html_message = f"""
                        <head>
                            <style>
                                h2, h3 {{ color: red; }}
                                h4 {{ color: rgb(173, 123, 0); }}
                                span {{ color: black; }}
                            </style>
                        </head>
                        <body>
                            <h2>REFVUGEE COMMENT REPORT FORM</h2>
                            <h4>Complaint By: <span>{reporter}</span></h4>
                            <h4>Complaint Against: <span>{reportee}</span></h4>
                            <h4>Post Title: <span>"{post}"</span></h4>
                            <h4>Comment Title: <span>"{comment}"</span></h4>
                            {replying_to_html_string}
                            <h4>Complaint Subject: <span>{subject}</span></h4>
                            <h4>Complaint Body: </h4>
                            <hr>    
                            <p>{complaint}</p>
                            <hr>
                            <h4>Link To Review Comment (you might have to sign in): <span>{review}</span></h4>
                            <h4>Link To Delete Comment (you might have to sign in): <span>{delete}</span></h4>
                            <br>
                            <h3>--Automated from Refvugee</h3>
                        </body>
                        """

        from_email = settings.EMAIL_HOST_USER
        recipient_list = []
        recipient_list_queryset = User.objects.filter(is_staff=True).all()

        for recipient in recipient_list_queryset:
            recipient_list += [recipient.email]

        send_mail(email_subject, message, from_email, recipient_list, html_message=html_message)


class ContactForm(forms.Form):
    subject = forms.CharField(max_length=50)
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 10, 'cols': 40}))

    def send_contact_email(self, subject, message, sender):
        html_message = f"""
                        <head>
                            <style>
                                h2, h3 {{ color: red; }}
                                h4 {{ color: rgb(173, 123, 0); }}
                                span {{ color: black; }}
                            </style>
                        </head>
                        <body>
                            <h2>REFVUGEE CONTACT FORM</h2>
                            <h4>Contact By: <span>{sender}</span></h4>
                            <h4>Contact Subject: <span>{subject}</span></h4>
                            <h4>Contact Message: </h4>
                            <hr>    
                            <p>{message}</p>
                            <hr>
                            <br>
                            <h3>--Automated from Refvugee</h3>
                        </body>
                        """
        from_email = settings.EMAIL_HOST_USER
        recipient_list_queryset = User.objects.filter(is_staff=True).all()
        recipient_list = []

        for recipient in recipient_list_queryset:
            recipient_list += [recipient.email]

        send_mail(subject, message, from_email, recipient_list, html_message=html_message)