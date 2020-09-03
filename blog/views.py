from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import (
    ListView,
    DetailView,
    CreateView, 
    UpdateView, 
    DeleteView, 
    FormView)
from django.contrib import messages
from .models import Post, Comment, Reply
from users.models import Profile
from .forms import CommentForm, ReportForm, ContactForm

# Max number of entries that will be shown on a single page
PAGINATE_BY_ENTRIES = 5

class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = PAGINATE_BY_ENTRIES

class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    paginate_by = PAGINATE_BY_ENTRIES

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')

class SearchPostListView(ListView):
    model = Post
    template_name = 'blog/search_results.html'
    context_object_name = 'posts'
    paginate_by = PAGINATE_BY_ENTRIES 
        
    def get_queryset(self):
        keywords_string = self.kwargs.get('query')
        keywords = keywords_string.split()
        if keywords and len(keywords) < 100:
            post_queryset = Post.objects.order_by('-date_posted').all()
            all_posts = []
            matching_posts = []

            for post in post_queryset:
                all_posts += [post]

            for post in all_posts:
                for word in keywords:
                    for post_word in post.keywords.split(','):
                        if word.lower() == post_word.lower():
                            matching_posts += [post]

        return matching_posts
    
class PostDetailView(DetailView):
    model = Post
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        curr_post_id = self.kwargs.get('pk')

        comments_queryset = Comment.objects.order_by('-date_posted').filter(post_id=curr_post_id).values()
        comments = []
        num_comments = 0
        num_replies = 0

        for comment in comments_queryset:
            num_comments += 1
            curr_comment_replies_queryset = Reply.objects.order_by('date_posted').filter(parent_comment_id=comment['id'])
            curr_comment_replies = []
            for reply in curr_comment_replies_queryset:
                num_replies += 1
                curr_comment_replies += [reply]
            comment_context = {
                'author': User.objects.get(id=comment['author_id']),
                'comment': comment,
                'replies': curr_comment_replies
            }
            comments += [comment_context]

        context['comments'] = comments
        context['num_comments'] = num_comments + num_replies
        return context


class PostCreateView(UserPassesTestMixin, LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'about', 'keywords', 'content']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['update'] = False
        
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'The post has been created and notifications have been sent.')
        return super().form_valid(form)

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'about', 'keywords', 'content']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['update'] = True
        
        return context

    def form_valid(self, form):
        messages.success(self.request, 'The post has been updated and notifications have been sent.')
        return super().form_valid(form)

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    context_object_name = 'post'
    success_url = '/'

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

class CommentDetailView(UserPassesTestMixin, LoginRequiredMixin, DetailView):
    model = Comment
    context_object_name = 'comment'

    def get_object(self):
        return Comment.objects.get(id=self.kwargs.get('id'))

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

class CommentCreateView(LoginRequiredMixin, FormView):
    model = Comment
    template_name = 'blog/comment_form.html'
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        curr_post_id = self.kwargs.get('pk')
        comments_queryset = Comment.objects.order_by('-date_posted').filter(post_id=curr_post_id).values()
        comments = []
        num_comments = 0
        num_replies = 0

        for comment in comments_queryset:
            num_comments += 1
            curr_comment_replies_queryset = Reply.objects.order_by('date_posted').filter(parent_comment_id=comment['id'])
            curr_comment_replies = []
            for reply in curr_comment_replies_queryset:
                num_replies += 1
                curr_comment_replies += [reply]
            comment_context = {
                'author': User.objects.get(id=comment['author_id']),
                'comment': comment,
                'replies': curr_comment_replies
            }
            comments += [comment_context]

        context['update'] = False
        context['post'] = Post.objects.get(pk=curr_post_id)
        context['comments'] = comments
        context['num_comments'] = num_comments + num_replies

        return context

    def form_valid(self, form):
        title = form.cleaned_data.get('title')
        content = form.cleaned_data.get('content')
        post = Post.objects.get(pk=self.kwargs.get('pk'))
        comment = Comment(title=title, content=content, post=post, author=self.request.user)
        comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        return f'/post/{self.kwargs.get("pk")}/'

class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        curr_post_id = self.kwargs.get('pk')
        comments_queryset = Comment.objects.order_by('-date_posted').filter(post_id=curr_post_id).values()
        comments = []
        num_comments = 0
        num_replies = 0

        for comment in comments_queryset:
            num_comments += 1
            curr_comment_replies_queryset = Reply.objects.order_by('date_posted').filter(parent_comment_id=comment['id'])
            curr_comment_replies = []
            for reply in curr_comment_replies_queryset:
                num_replies += 1
                curr_comment_replies += [reply]
            comment_context = {
                'author': User.objects.get(id=comment['author_id']),
                'comment': comment,
                'replies': curr_comment_replies
            }
            comments += [comment_context]

        context['update'] = True
        context['post'] = Post.objects.get(pk=curr_post_id)
        context['comments'] = comments
        context['num_comments'] = num_comments + num_replies

        return context

    def get_object(self):
        return Comment.objects.get(id=self.kwargs.get('id'))

    def test_func(self):
        comment = self.get_object()
        if self.request.user.id == comment.author_id or self.request.user.is_staff:
            return True
        return False

    def get_success_url(self):
        return f'/post/{self.kwargs.get("pk")}/'

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    context_object_name = 'comment'

    def get_object(self):
        return Comment.objects.get(id=self.kwargs.get('id'))
    
    def get_success_url(self):
        return f'/post/{self.kwargs.get("pk")}/'

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

class CommentReportView(UserPassesTestMixin, LoginRequiredMixin, FormView):
    template_name = 'blog/report_form.html'
    form_class = ReportForm

    def get(self, request, *args, **kwargs):
        if self.request.user.id == Comment.objects.filter(id=self.kwargs.get('id')).values()[0]['author_id']:
            messages.warning(self.request, 'You can not report a comment that you made.')
            return redirect(self.get_success_url()) 

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        subject = form.cleaned_data['subject']
        complaint = form.cleaned_data['complaint']
        reporter_name = self.request.user.username
        reported_comment = Comment.objects.filter(id=self.kwargs.get('id')).values()[0]
        reportee_name = User.objects.get(id=reported_comment['author_id']).username
        post_title = Post.objects.filter(pk=self.kwargs.get('pk')).values()[0]['title']
        comment_title = Comment.objects.filter(id=self.kwargs.get('id')).values()[0]['title']
        review_link = f'http://127.0.0.1:8000/post/{self.kwargs.get("pk")}/comment/{self.kwargs.get("id")}/'
        delete_link = f'http://127.0.0.1:8000/post/{self.kwargs.get("pk")}/comment/{self.kwargs.get("id")}/delete/'       
        
        form.send_report_email(subject, complaint, reporter_name, reportee_name, post_title, comment_title, review_link, delete_link)

        messages.success(self.request, 'Your report was sent successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Your report failed to send.')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return f'/post/{self.kwargs.get("pk")}/'

    def test_func(self):
        if self.request.user.id == Comment.objects.filter(id=self.kwargs.get('id')).values()[0]['author_id']:
            return False
        return True

class ReplyDetailView(UserPassesTestMixin, LoginRequiredMixin, DetailView):
    model = Reply
    context_object_name = 'reply'

    def get_object(self):
        return Reply.objects.get(id=self.kwargs.get('key'))

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

class ReplyCreateView(LoginRequiredMixin, FormView):
    model = Reply
    template_name = 'blog/reply_form.html'
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        curr_post_id = self.kwargs.get('pk')
        comments_queryset = Comment.objects.order_by('-date_posted').filter(post_id=curr_post_id).values()
        comments = []
        num_comments = 0
        num_replies = 0

        for comment in comments_queryset:
            num_comments += 1
            curr_comment_replies_queryset = Reply.objects.order_by('date_posted').filter(parent_comment_id=comment['id'])
            curr_comment_replies = []
            for reply in curr_comment_replies_queryset:
                num_replies += 1
                curr_comment_replies += [reply]
            comment_context = {
                'author': User.objects.get(id=comment['author_id']),
                'comment': comment,
                'replies': curr_comment_replies
            }
            comments += [comment_context]

        context['update'] = False
        context['post'] = Post.objects.get(pk=curr_post_id)
        context['comments'] = comments
        context['num_comments'] = num_comments + num_replies

        return context

    def form_valid(self, form):
        title = form.cleaned_data.get('title')
        content = form.cleaned_data.get('content')
        parent_comment = Comment.objects.get(id=self.kwargs.get('id'))
        reply = Reply(title=title, content=content, parent_comment=parent_comment, author=self.request.user)
        reply.save()
        return super().form_valid(form)

    def get_success_url(self):
        return f'/post/{self.kwargs.get("pk")}/'

class ReplyUpdateView(UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    model = Reply
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        curr_post_id = self.kwargs.get('pk')
        comments_queryset = Comment.objects.order_by('-date_posted').filter(post_id=curr_post_id).values()
        comments = []
        num_comments = 0
        num_replies =0

        for comment in comments_queryset:
            num_comments += 1
            curr_comment_replies_queryset = Reply.objects.order_by('date_posted').filter(parent_comment_id=comment['id'])
            curr_comment_replies = []
            for reply in curr_comment_replies_queryset:
                num_replies += 1
                curr_comment_replies += [reply]
            comment_context = {
                'author': User.objects.get(id=comment['author_id']),
                'comment': comment,
                'replies': curr_comment_replies
            }
            comments += [comment_context]

        context['update'] = True
        context['post'] = Post.objects.get(pk=curr_post_id)
        context['comments'] = comments
        context['num_comments'] = num_comments + num_replies

        return context

    def get_object(self):
        return Reply.objects.get(id=self.kwargs.get('key'))

    def get_success_url(self):
        return f'/post/{self.kwargs.get("pk")}/'

    def test_func(self):
        reply = self.get_object()
        if self.request.user.id == reply.author_id or self.request.user.is_staff:
            return True
        return False
        

class ReplyDeleteView(UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    model = Reply
    context_object_name = 'reply'
    template_name = 'blog/comment_confirm_delete.html'

    def get_object(self):
        return Reply.objects.get(id=self.kwargs.get('key'))
    
    def get_success_url(self):
        return f'/post/{self.kwargs.get("pk")}/'

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

class ReplyReportView(UserPassesTestMixin, LoginRequiredMixin, FormView):
    template_name = 'blog/report_form.html'
    form_class = ReportForm

    def get(self, request, *args, **kwargs):
        if self.request.user.id == Reply.objects.filter(id=self.kwargs.get('key')).values()[0]['author_id']:
            messages.warning(self.request, 'You can not report a comment that you made.')
            return redirect(self.get_success_url()) 

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        subject = form.cleaned_data['subject']
        complaint = form.cleaned_data['complaint']
        reporter_name = self.request.user.username
        reported_comment = Reply.objects.filter(id=self.kwargs.get('key')).values()[0]
        reportee_name = User.objects.get(id=reported_comment['author_id']).username
        post_title = Post.objects.filter(pk=self.kwargs.get('pk')).values()[0]['title']
        comment_title = Reply.objects.filter(id=self.kwargs.get('key')).values()[0]['title']
        parent_comment = Comment.objects.get(id=reported_comment['parent_comment_id'])
        review_link = f'http://127.0.0.1:8000/post/{self.kwargs.get("pk")}/comment/{self.kwargs.get("id")}/reply/{self.kwargs.get("key")}'
        delete_link = f'http://127.0.0.1:8000/post/{self.kwargs.get("pk")}/comment/{self.kwargs.get("id")}/reply/{self.kwargs.get("key")}/delete/'       
        
        form.send_report_email(subject, complaint, reporter_name, reportee_name, post_title, comment_title,
         review_link, delete_link, parent_comment=parent_comment)

        messages.success(self.request, 'Your report was sent successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Your report failed to send.')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return f'/post/{self.kwargs.get("pk")}/'

    def test_func(self):
        if self.request.user.id == Reply.objects.filter(id=self.kwargs.get('key')).values()[0]['author_id']:
            return False
        return True

class ContactView(LoginRequiredMixin, FormView):
    template_name = 'blog/contact_form.html'
    form_class = ContactForm
    success_url = '/'

    def form_valid(self, form):
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']
        sender = self.request.user.username

        form.send_contact_email(subject, message, sender)

        messages.success(self.request, 'We have received your message!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Your message failed to send.')
        return redirect('blog-home')

def about(request):
    return render(request, 'blog/about.html')

def calendar(request):
    return render(request, 'blog/calendar.html')

def announcements(request):
    return render(request, 'blog/announcements.html')

def upcoming_events(request):
    return render(request, 'blog/upcoming_events.html')

def search(request):
    if request.method == 'POST':
        keywords = request.POST['query']
        if keywords and len(keywords) < 100:           
            return redirect(reverse('search-results', kwargs={'query': keywords}))
        else:
            messages.error(request, 'Your search query was invalid.')
            return redirect('blog-home')
    else:
        return redirect('blog-home')

@login_required
def mailing_list_detail(request):
    if request.method == 'GET':
        return render(request, 'blog/mailing_list_detail.html')
    else:
        return redirect('blog-home')

@login_required
def mailing_list_subscribe(request):
    if not request.user.profile.notify and request.method == 'GET':
        return render(request, 'blog/mailing_list_subscribe.html')
    else:
        return redirect('blog-home')

@login_required
def mailing_list_unsubscribe(request):
    if request.user.profile.notify and request.method == 'GET':
        return render(request, 'blog/mailing_list_unsubscribe.html')
    else:
        return redirect('blog-home')

@login_required
def mailing_list_subscribe_done(request):
    if not request.user.profile.notify and request.method == 'POST':
        request.user.profile.notify = True
        request.user.profile.save()
        messages.success(request, 'You have been successfully subscribed to our mailing list!')
        return redirect('blog-home')
    else:
        return redirect('blog-home')

@login_required
def mailing_list_unsubscribe_done(request):
    if request.user.profile.notify and request.method == 'POST':
        request.user.profile.notify = False
        request.user.profile.save()
        messages.success(request, 'You have been successfully unsubscribed from our mailing list.')
        return redirect('blog-home')
    else:
        return redirect('blog-home')
