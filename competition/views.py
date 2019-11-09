import csv
from decimal import Decimal
from operator import itemgetter

from django.conf import settings
from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from django.shortcuts import reverse
from django.views.generic import DetailView, FormView, ListView, View
from django.views.generic.detail import SingleObjectMixin

from participant.models import Team

from .forms import InitializeCompetitionForm, SubmitForm
from .models import Event, ProblemCategory, Solution


class EventListView(ListView):
    model = Event
    context_object_name = 'events'

    template_name = 'competition/index.html'


class EventDetailView(DetailView):
    model = Event
    context_object_name = 'event'

    template_name = 'competition/event.html'


class InitializeCompetitionView(FormView):
    template_name = 'competition/initialize_competition.html'

    form_class = InitializeCompetitionForm

    def get_success_url(self):
        return reverse('competition:index')

    def form_valid(self, form):
        event = form.save()

        messages.success(
            self.request, '{} bol úspešne vytvorený!'.format(event))

        return super(InitializeCompetitionView, self).form_valid(form)


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
            'Úloha {} {} bola úspešne odovzdaná tímom {} zo školy {}.'.format(
                solution.problem_category.name.lower(),
                solution.problem_position,
                solution.team.name,
                solution.team.school))

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
                    'count': team.solution_set.filter(problem_category=category).count(),
                } for category in categories
            ],
            'points': Decimal(0),
            'problem_points': Decimal(0)
        } for team in Team.objects.filter(event=event)
    ]

    # Compute points

    for team in teams:
        for category_stats, category in zip(team['categories'], categories):
            if category.multiplicative_compensation:
                category_points = category_stats['count'] * \
                    category_stats['points']*team['compensation']
            else:
                category_points = category_stats['count'] * \
                    category_stats['points']

            team['points'] += category_points

            if category.is_problem:
                team['problem_points'] += category_points

        if event.flat_compensation:
            team['points'] += team['compensation']

    # for team in teams:
    #     team['problem_points'] = sum(
    #         [category['points'] * category['count']
    #          for category in team['categories']]
    #     )
    #     team['points'] = team['problem_points'] + team['compensation']

    # Sort teams
    team_comparator = itemgetter('points', 'problem_points')
    teams.sort(key=team_comparator, reverse=True)

    # Generate ranks
    def save_team_ranks(teams, lower_rank):
        upper_rank = lower_rank + len(teams) - 1

        if len(teams) == 1:
            teams[0]['rank'] = lower_rank
        else:
            for team_to_rank in teams:
                team_to_rank['rank'] = "{} - {}".format(lower_rank, upper_rank)

        return upper_rank

    lower_rank = 1
    identically_ranked_teams = []

    for team in teams:
        if not identically_ranked_teams or\
                team_comparator(team) == team_comparator(identically_ranked_teams[-1]):
            identically_ranked_teams.append(team)
        else:
            lower_rank = save_team_ranks(
                identically_ranked_teams, lower_rank) + 1

            identically_ranked_teams.clear()
            identically_ranked_teams.append(team)

    save_team_ranks(identically_ranked_teams, lower_rank)

    return (categories, teams)
