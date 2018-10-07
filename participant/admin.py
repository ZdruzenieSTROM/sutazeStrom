from django.contrib import admin

from .models import Compensation, Participant, Team

admin.site.register(Compensation)
admin.site.register(Participant)
admin.site.register(Team)
