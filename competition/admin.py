from django.contrib import admin
from .models import Problem, Competition, Event, Solution

admin.site.register(Problem)
admin.site.register(Event)
admin.site.register(Competition)
admin.site.register(Solution)
