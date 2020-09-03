from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden, Http404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm


def register(request):
    form = None
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
            else:
                raise Http404('We were not able to sign you in')
            messages.success(request, 'Your account has been created and you have been logged in!')
            messages.info(request, 'Go to your profile to add a profile picture!')
            return redirect('mailing-list-detail')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    u_form, p_form = None, None
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm()

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'users/profile.html', context)

class UserLoginView(LoginView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseForbidden("""
                                        <style>
                                            h1 { color: red; }
                                            a { color: rgb(173, 123, 0); text-decoration: none; }
                                        </style>
                                        <h1>403 Forbidden</h1>
                                        <hr>
                                        <h3>You are already signed in.</h3>
                                        <h3>Sign out <a href="http://127.0.0.1:8000/logout/">here</a></h3>
                                        """)
        return super().get(request, *args, **kwargs)

def logout_view(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            logout(request)
            return render(request, 'users/logout.html')
        else:
            return HttpResponseForbidden("""
                                        <style>
                                            h1 { color: red; }
                                            a { color: rgb(173, 123, 0); text-decoration: none; }
                                        </style>
                                        <h1>403 Forbidden</h1>
                                        <hr>
                                        <h3>You were not signed in.</h3>
                                        <h3>Sign in <a href="http://127.0.0.1:8000/login/">here</a></h3>
                                        """)
    else:
        raise Http404('You can not post to this page')
