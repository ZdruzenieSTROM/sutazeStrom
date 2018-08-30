from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.contrib import admin
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from .models import *

def index(request):
    template = 'competition/index.html'
    return render(request, template, {})

def log_out(request):
    logout(request)
    return redirect('competition:index')
