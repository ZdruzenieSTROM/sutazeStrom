from django.contrib import admin

from .models import Participant, School, Team

admin.site.register(Team)
admin.site.register(School)
admin.site.register(Participant)
