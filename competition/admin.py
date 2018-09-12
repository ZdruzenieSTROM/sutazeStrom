from django.contrib import admin

from .models import Event, Problem, Solution

admin.site.register(Problem)
admin.site.register(Event)
admin.site.register(Solution)
