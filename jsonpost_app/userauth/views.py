# Create your views here.

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        print('first')
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('view_posts')  # or your post route
        else:
            messages.error(request, "Invalid credentials.")
    return render(request, 'userauth/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')
