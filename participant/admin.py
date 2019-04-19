from django.contrib import admin

from .models import Compensation, Participant, Team


class ParticipantInline(admin.TabularInline):
    model = Participant
    extra = 0

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):

        if kwargs:
            t = Team.objects.get(
                pk=resolve(request.path_info).kwargs['object_id']
            )

            kwargs['queryset'] = Participant.objects.filter(team=t)

        return super(ParticipantInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'event')
    readonly_fields = ('number',)
    list_filter = ('event',)
    list_per_page = 100

    inlines = [ParticipantInline]

    search_fields = [
        'name',
        'school',
    ]
    ordering = ('number', '-pk')


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('team', 'first_name', 'last_name', 'compensation')
    list_per_page = 100

    search_fields = [
        'first_name',
        'last_name',
    ]
    ordering = ('last_name', 'first_name', '-pk')

admin.site.register(Compensation)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Team, TeamAdmin)
