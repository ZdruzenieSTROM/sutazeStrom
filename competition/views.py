from operator import itemgetter

from django.conf import settings
from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.shortcuts import reverse
from django.views.generic import DetailView, FormView, ListView
from django.views.generic.detail import SingleObjectMixin

from participant.models import Team

from .forms import SubmitForm
from .models import Event, ProblemCategory, Solution


class EventListView(ListView):
    model = Event
    context_object_name = 'events'

    template_name = 'competition/index.html'


class EventDetailView(DetailView):
    model = Event
    context_object_name = 'event'

    template_name = 'competition/event.html'


class SubmitFormView(FormView, SingleObjectMixin):
    model = Event
    context_object_name = 'event'

    template_name = 'competition/submit.html'

    form_class = SubmitForm

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        return super(SubmitFormView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('competition:submit', kwargs={'pk': self.kwargs['pk']})

    def get_initial(self):
        return {'event': self.object}

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

        results = generate_results(self.object)
        context['categories'], context['teams'] = results[0], results[1]

        return context


class CSVResultsView(DetailView):
    model = Event
    context_object_name = 'event'

    template_name = 'competition/results.csv'

    def get_context_data(self, **kwargs):
        context = super(CSVResultsView, self).get_context_data(**kwargs)

        results = generate_results(self.object)
        context['categories'], context['teams'] = results[0], results[1]

        context['delimiter'] = settings.CSV_DELIMITER

        return context


def generate_results(event):
    categories = ProblemCategory.objects.filter(
        event=event).order_by('position')

    teams = [
        {
            'name': team.name,
            'school': team.school,
            # TODO: sort members alphabetically
            'members': ', '.join([
                '{} {}'.format(member.first_name, member.last_name)
                for member in team.participant_set.all()
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

    for team in teams:
        team['problem_points'] = sum(
            [category['points'] * category['count']
                for category in team['categories']]
        )
        team['points'] = team['problem_points'] + team['compensation']

    comp = itemgetter('points', 'problem_points')

    teams = sorted(
        teams,
        key=comp,
        reverse=True
    )

    place = 1

    for i in range(len(teams)):
        teams[i]['place'] = place

        if i < len(teams)-1 and comp(teams[i]) != comp(teams[i+1]):
            place += 1

    return (categories, teams)
