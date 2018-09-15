from django.contrib import admin

from .models import Compensation, Event, Problem, Solution

admin.site.register(Compensation)
admin.site.register(Event)
admin.site.register(Problem)
admin.site.register(Solution)
