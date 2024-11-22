import csv
import json
from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.core import management
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.views import View
from django.views.generic import DetailView, FormView, ListView, View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormView

from datetime import timedelta

from .forms import ImportForm, InitializeForm, SubmitForm
from .models import Event, ProblemCategory, Solution, Team
from .results import generate_results

# pylint: disable=attribute-defined-outside-init,unused-argument


def nonstaff_redirect_to_public_results(view_func):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapper_view(request, *args, **kwargs):
            if request.user.is_staff:
                return view_func(request, *args, **kwargs)
            return redirect('competition:public-results-latest')

        return _wrapper_view
    return decorator(view_func)


def view_404(request, exception=None):  # pylint: disable=unused-argument
    """Presmerovanie 404 na homepage"""
    return redirect('competition:public-results-latest')


class SingleObjectFormView(FormView, SingleObjectMixin):
    object_field_name = None

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

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

    def post(self, request, pk):
        """Start event"""
        self.object = self.get_object()
        if self.object.started_at is None:
            self.object.started_at = now()
            self.object.save()
        return self.get(request=request, pk=pk)


class InitializeView(FormView):
    template_name = 'competition/initialize.html'

    form_class = InitializeForm
    success_url = reverse_lazy('competition:index')

    def form_valid(self, form):
        event = form.save()

        messages.success(self.request, f'{ event } bol úspešne vytvorený!')

        return super().form_valid(form)


class SubmitFormView(SingleObjectFormView):
    model = Event
    context_object_name = 'event'

    template_name = 'competition/submit.html'

    form_class = SubmitForm

    object_field_name = 'event'

    def get_success_url(self):
        return reverse('competition:submit', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

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

        return super().form_valid(form)

    def form_invalid(self, form):
        data = form.data.copy()
        data['code'] = ''
        form.data = data

        return super().form_invalid(form)


class ResultsView(DetailView):
    model = Event
    context_object_name = 'event'

    template_name = 'competition/results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'], context['teams'] = generate_results(self.object)
        return context

    def serialize_results(self, results):
        for team in results:
            team['compensation'] = str(team['compensation'])
            team['total_points'] = str(team['total_points'])
            team['problem_points'] = str(team['problem_points'])
            if team['spare_time'] is not None:
                team['spare_time'] = team['spare_time'].total_seconds()
        return json.dumps(results)

    def post(self, request, pk):
        if not request.user.is_staff:
            raise PermissionDenied()
        self.object: Event = self.get_object()
        # self.request.POST['freeze'] is always a string and even "False" evaluates to True
        if self.request.POST['freeze'] == "True":
            _, results = generate_results(self.object)
            self.object.frozen_results = self.serialize_results(results)
        else:
            self.object.frozen_results = None
        self.object.save()
        return self.get(request, pk=pk)


class PublicResultsView(ResultsView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.frozen_results is not None:
            context['teams'] = json.loads(self.object.frozen_results)
            for team in context['teams']:
                if team['spare_time'] is not None:
                    team['spare_time'] = timedelta(seconds=team['spare_time'])
        return context


class LatestPublicResultsView(ResultsView):
    def get_object(self):
        return Event.objects.latest()


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


class CertificatesView(DetailView):
    """Generovanie latex vstupu pre diplomy"""
    model = Event
    context_object_name = 'event'

    template_name = 'competition/certificates.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        _, teams = generate_results(self.object)
        context['team_certificates'] = map(
            self.format_team_certificate, teams)
        context['members_certificates'] = map(
            self.format_members_certificate, teams)
        return context

    @staticmethod
    def format_rank(rank: str) -> str:
        if isinstance(rank, str):
            return rank.split('-')[0].strip()
        return rank

    @staticmethod
    def format_members(members: str) -> str:
        members = members.split(',')
        if len(members) > 1:
            return ' \\& '.join([', '.join(members[:-1]), members[-1]])
        return members

    @classmethod
    def format_team_certificate(cls, team: dict) -> str:
        members = cls.format_members(team['members'])
        rank = cls.format_rank(team['rank'])
        return f'\\diplom{{{rank}}}{{{team["school"]}}}{{{members}}}'

    @classmethod
    def format_members_certificate(cls, team: dict) -> list[str]:
        members: list[str] = team['members'].split(',')
        rank = cls.format_rank(team['rank'])
        return [f'\\diplom{{{rank}}}{{{member.strip()}}}{{}}' for member in members]


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

        return super().form_valid(form)


class StatisticsView(DetailView):
    model = Event
    context_object_name = 'event'
    template_name = 'competition/statistics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        categories = ProblemCategory.objects.filter(event=self.object).all()
        problem_statistics = {}
        for category in categories:
            solutions = Solution.objects.filter(
                team__event=self.object,
                problem_category=category
            ).all()
            number_of_teams = Team.objects.filter(event=self.object).count()
            stats = []
            for _ in range(number_of_teams):
                stats.append([0]*category.problem_count)
            for solution in solutions:
                # TODO: Tie operacie so 100 vyzeraju dost nebezpecne,
                # to by mozno bolo dobre vytiahnut do osobitnych metod
                stats[solution.team.number-100][solution.problem_position-1] = 1

            problem_statistics[category.name] = {
                'stats': stats,
                'problems': list(range(category.problem_count))
            }
        context['stats'] = problem_statistics
        context['number_of_teams'] = number_of_teams
        return context


class StatisticsCsvExportView(StatisticsView):
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export.csv"'

        writer = csv.writer(response, delimiter=settings.CSV_DELIMITER)
        joined_header = ['Číslo tímu']
        joined_stats = [[] for _ in range(context['number_of_teams'])]
        for category_name, category_stats in context['stats'].items():
            joined_header.extend(
                [f'{category_name[:3]} {i+1}.' for i in category_stats['problems']])
            for i, team_stats in enumerate(category_stats['stats']):
                joined_stats[i].extend(team_stats)

        writer.writerow(joined_header)
        for i, team in enumerate(joined_stats):
            row = [i]
            row.extend(team)
            writer.writerow(row)
        return response


class ExportView(View):
    def get(self, request):
        management.call_command('dumpdata', format='json', output='db.json')

        return FileResponse(open('db.json', 'rb'), as_attachment=True)
