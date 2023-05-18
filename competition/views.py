import csv
from decimal import Decimal
import json
from operator import itemgetter

from django.conf import settings
from django.contrib import messages
from django.core import management
from django.db.models import Count, Q, Sum
from django.http import FileResponse, HttpResponse
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import DetailView, FormView, ListView, View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormView
from django.utils.timezone import now

from .forms import ImportForm, InitializeForm, SubmitForm
from .models import Event, ProblemCategory, Solution, Team


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


class EventListView(ListView):
    model = Event
    context_object_name = 'events'

    template_name = 'competition/index.html'


class EventDetailView(DetailView):
    model = Event
    context_object_name = 'event'

    template_name = 'competition/event.html'

    def post(self,request,pk):
        """Start event"""
        self.object = self.get_object()
        if self.object.started_at is None:
            self.object.started_at = now()
            self.object.save()
        return self.get(request=request,pk=pk)


class InitializeView(FormView):
    template_name = 'competition/initialize.html'

    form_class = InitializeForm
    success_url = reverse_lazy('competition:index')

    def form_valid(self, form):
        event = form.save()

        messages.success(self.request, f'{ event } bol úspešne vytvorený!')

        return super(InitializeView, self).form_valid(form)


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
            f'Úloha { solution.problem_category.name.lower() } '
            f'{ solution.problem_position } '
            f'bola úspešne odovzdaná tímom { solution.team.name } '
            f'zo školy { solution.team.school }.')

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
    
    def serialize_results(self,results):
        for team in results:
            team['total_points'] = str(team['total_points'])
            team['problem_points'] = str(team['problem_points'])
        return json.dumps(results)
    
    def post(self,request,pk):
        if request.user.is_staff:
            self.object = self.get_object()
            if self.request.POST['freeze'] == "True":  # self.request.POST['freeze'] is always a string and even "False" evaluates to True
                _, results = generate_results(self.object)
                self.object.frozen_results = self.serialize_results(results)
            else:
                self.object.frozen_results = None
            self.object.save()
            return self.get(request,pk=pk)

class PublicResultsView(ResultsView):
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.frozen_results is not None:
            context['teams'] = self.object.frozen_results
        return context

class CSVResultsView(View, SingleObjectMixin):
    model = Event
    context_object_name = 'event'

    def get(self, request, pk):
        self.object = self.get_object()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export.csv"'

        categories, teams = generate_results(self.object)

        writer = csv.writer(response, delimiter=settings.CSV_DELIMITER)

        heading = ['Poradie', 'Názov tímu',
                   'Škola', 'Účastníci', 'Bonifikácia']
        heading.extend([category.name for category in categories])
        heading.extend(['Úlohy', 'Spolu'])

        writer.writerow(heading)

        for team in teams:
            row = [team['rank'], team['name'], team['school'],
                   team['members'], team['compensation']]
            row.extend(team['solved_by_category'])
            row.extend([team['problem_points'], team['total_points']])

            writer.writerow(row)

        return response


class ImportFormView(FormView):
    form_class = ImportForm

    template_name = 'competition/import.html'

    def get_success_url(self):
        return reverse('competition:import')

    def form_valid(self, form):
        saved = form.save()

        messages.success(
            self.request,
            f'Údaje boli úspešne importované. Počet tímov: { saved["teams"] },'
            f' počet účastníkov: { saved["participants"] }')

        return super(ImportFormView, self).form_valid(form)


class ExportView(View):
    def get(self, request):
        management.call_command('dumpdata', format='json', output='db.json')

        return FileResponse(open('db.json', 'rb'), as_attachment=True)


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
                f'{ member.first_name } { member.last_name }'
                for member in team.participant_set.order_by('last_name', 'first_name')
            ]),
            **team.participant_set.aggregate(compensation=Sum('compensation__points')),
            'solved_by_category': [
                team.solution_set.filter(problem_category=category).count()
                for category in categories
            ],
            'total_points': Decimal(0),
            'problem_points': Decimal(0),
            'solved_problems': 0,
        } for team in Team.objects.filter(event=event)
    ]

    # Compute points

    for team in teams:
        for count, category in zip(team['solved_by_category'], categories):
            if category.multiplicative_compensation:
                category_points = count * \
                    category.points*team['compensation']
            else:
                category_points = count * \
                    category.points

            team['total_points'] += category_points

            if category.is_problem:
                team['solved_problems'] += count
                team['problem_points'] += category_points

        if event.flat_compensation:
            team['total_points'] += team['compensation']

    # Sort teams
    if event.name == 'LOMIHLAV':
        team_key = itemgetter('total_points', 'solved_problems')
    else:
        team_key = itemgetter('total_points', 'problem_points')

    teams.sort(key=team_key, reverse=True)

    # Generate ranks
    def save_team_ranks(teams, lower_rank):
        upper_rank = lower_rank + len(teams) - 1

        if len(teams) == 1:
            teams[0]['rank'] = lower_rank
        else:
            for team_to_rank in teams:
                team_to_rank['rank'] = f'{ lower_rank } - { upper_rank }'

        return upper_rank

    lower_rank = 1
    identically_ranked_teams = []

    for team in teams:
        if not identically_ranked_teams or\
                team_key(team) == team_key(identically_ranked_teams[-1]):
            identically_ranked_teams.append(team)
        else:
            lower_rank = save_team_ranks(
                identically_ranked_teams, lower_rank) + 1

            identically_ranked_teams.clear()
            identically_ranked_teams.append(team)

    save_team_ranks(identically_ranked_teams, lower_rank)

    return (categories, teams)
