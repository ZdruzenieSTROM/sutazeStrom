from django.contrib import admin

from .models import (Compensation, Event, Participant, ProblemCategory,
                     Solution, Team)


@admin.register(ProblemCategory)
class ProblemCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'problem_count', 'points',)

    ordering = ('event', 'position',)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'number', 'school', 'event',)
    list_filter = ('event',)
    list_per_page = 100

    class ParticipantInline(admin.TabularInline):
        model = Participant
        extra = 0

    def get_readonly_fields(self, request, obj=None):
        # Number is read-only after creation, but can be entered during
        # creation (obj is None).
        if obj:
            return ["number"]
        else:
            return []
    inlines = (ParticipantInline,)

    search_fields = ('name', 'school', 'number',)
    ordering = ('number', '-pk',)


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'team', 'compensation',)
    list_per_page = 100

    search_fields = ('first_name', 'last_name',)

    ordering = ('last_name', 'first_name', '-pk',)


admin.site.register(Event)
admin.site.register(Solution)
admin.site.register(Compensation)
