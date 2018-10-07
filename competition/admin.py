from django.contrib import admin

from .models import Event, Problem, ProblemCategory, Solution

admin.site.register(Event)
admin.site.register(Problem)
admin.site.register(ProblemCategory)
admin.site.register(Solution)
