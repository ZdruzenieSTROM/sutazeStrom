import csv
from operator import itemgetter

from django.conf import settings
from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from django.shortcuts import reverse
from django.views.generic import DetailView, FormView, ListView, View
from django.views.generic.detail import SingleObjectMixin

from participant.models import Team

from .forms import InitializeMamutForm, SubmitForm
from .models import Event, ProblemCategory, Solution


class EventListView(ListView):
    model = Event
    context_object_name = 'events'

    template_name = 'competition/index.html'


class EventDetailView(DetailView):
    model = Event
    context_object_name = 'event'

    template_name = 'competition/event.html'


class InitializeMamutView(FormView):
    template_name = 'competition/initialize_mamut.html'

    form_class = InitializeMamutForm

    def get_success_url(self):
        return reverse('competition:index')

    def form_valid(self, form):
        event = form.save()

        messages.success(
            self.request, '{} bol úspešne vytvorený!'.format(event))

        return super(InitializeMamutView, self).form_valid(form)


class SingleObjectFormView(FormView, SingleObjectMixin):
    object_field_name = None

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        return super(SingleObjectFormView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(SingleObjectFormView, self).get_form_kwargs()

        if self.request.method in ('POST', 'PUT'):
            data = kwargs['data'].copy()
            data[self.object_field_name] = str(self.object.pk)
            kwargs['data'] = data

        if self.request.method == 'GET':
            kwargs['initial'].update({self.object_field_name: self.object})

        return kwargs


class SubmitFormView(SingleObjectFormView):
    model = Event
    context_object_name = 'event'

    template_name = 'competition/submit.html'

    form_class = SubmitForm

    object_field_name = 'event'

    def get_success_url(self):
        return reverse('competition:submit', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super(SubmitFormView, self).get_context_data(**kwargs)

        context['solutions'] = Solution.objects.filter(
            team__event=self.object).order_by('-time')[:10]

        return context

    def form_valid(self, form):
        solution = form.save()

        messages.success(
            self.request,
            'Úloha {} bola úspešne odovzdaná tímom {} zo školy {}.'.format(
                solution.problem.position,
                solution.team.name,
                solution.team.school
            )
        )

        return super(SubmitFormView, self).form_valid(form)

    def form_invalid(self, form):
        data = form.data.copy()
        data['code'] = ''
        form.data = data

        return super(SubmitFormView, self).form_invalid(form)


class ResultsView(DetailView):
    model = Event
    context_object_name = 'event'

    template_name = 'competition/results.html'

    def get_context_data(self, **kwargs):
        context = super(ResultsView, self).get_context_data(**kwargs)

        context['categories'], context['teams'] = generate_results(self.object)

        return context


class CSVResultsView(View, SingleObjectMixin):
    model = Event
    context_object_name = 'event'

    def get(self, request, pk):
        self.object = self.get_object()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export.csv"'

        _, teams = generate_results(self.object)

        writer = csv.writer(response, delimiter=settings.CSV_DELIMITER)

        for team in teams:
            row = [team['rank'], team['name'], team['school'],
                   team['members'], team['compensation']]
            row.extend([category['count'] for category in team['categories']])
            row.extend([team['problem_points'], team['points']])

            writer.writerow(row)

        return response


def generate_results(event):
    categories = ProblemCategory.objects.filter(
        event=event).order_by('position')

    # Pull information about teams from database
    # TODO: use annotate instead of pulling data into a dictionary
    teams = [
        {
            'name': team.name,
            'school': team.school,
            'members': ', '.join([
                '{} {}'.format(member.first_name, member.last_name)
                for member in team.participant_set.order_by('last_name', 'first_name')
            ]),
            **team.participant_set.aggregate(compensation=Sum('compensation__points')),
            'categories': [
                {
                    'points': category.points,
                    **team.solution_set.aggregate(
                        count=Count('problem', filter=Q(
                            problem__category=category))
                    )
                } for category in categories
            ]
        } for team in Team.objects.filter(event=event)
    ]

    # Compute points
    for team in teams:
        team['problem_points'] = sum(
            [category['points'] * category['count']
             for category in team['categories']]
        )
        team['points'] = team['problem_points'] + team['compensation']

    # Sort teams
    comp = itemgetter('points', 'problem_points')
    teams.sort(key=comp, reverse=True)

    # Generate ranks
    rank = 1

    for i, _ in enumerate(teams[:-1]):
        teams[i]['rank'] = rank

        if comp(teams[i]) != comp(teams[i+1]):
            rank += 1

    if teams:
        teams[-1]['rank'] = rank

    return (categories, teams)
