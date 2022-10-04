from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate, login, logout


class LoginView(TemplateView):

    template_name: str = 'core/login.html'

    def get(self, request, *args, **kwargs) -> render:
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs) -> redirect:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'core/login.html', {'error': 'Invalid Credentials'})


def logout_view(request) -> redirect:
    logout(request)
    return redirect('login')