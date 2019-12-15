from django.shortcuts import render
from django.views.generic import View
from social_network_app import forms
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, HttpResponseForbidden


class IndexView(View):
    def get(self, request):
        return render(request, 'index.html', {})


class RegisterView(View):
    user_form = forms.UserForm()

    def get(self, request):
        return render(request, 'register.html', {'user_form': self.user_form})

    def post(self, request):
        self.user_form = forms.UserForm(data=request.POST)
        # if user input is valid then new user will be created
        if self.user_form.is_valid():
            user = self.user_form.save(commit=False)
            user.set_password(self.user_form.cleaned_data['password'])
            user.username = self.user_form.cleaned_data['email'].lower()
            # user.is_active = False
            user.save()

            return HttpResponseRedirect(reverse('social_network_app:login'))
        else:
            # user input is not valid
            print(self.user_form.errors)
            return render(request, 'register.html', {'user_form': self.user_form})


class LoginView(View):
    login_form = forms.LoginForm()

    def get(self, request):
        return render(request, 'login.html', {'login_form': self.login_form})

    def post(self, request):
        self.login_form = forms.LoginForm(data=request.POST)
        if self.login_form.is_valid():
            user = authenticate(username=self.login_form.cleaned_data['email'], password=self.login_form.cleaned_data['password'])
            if user and user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
        else:
            print('Login failed')
            return HttpResponse("invalid login details")


class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('index'))
