from django.contrib import admin

from .models import Event, ProblemCategory, Solution

admin.site.register(Event)
admin.site.register(ProblemCategory)
admin.site.register(Solution)
