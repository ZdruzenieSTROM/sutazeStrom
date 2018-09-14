from functools import reduce

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.generic import DetailView, FormView, ListView, TemplateView
from django.views.generic.detail import SingleObjectMixin

from participant.models import Team

from .forms import SubmitForm
from .models import Event, Problem, Solution
from .queries import results_query

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

        return super(SubmitFormView, self).post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('competition:submit', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        event = get_object_or_404(Event, pk=int(self.kwargs['pk']))
        code = form.cleaned_data['code']

        convert = lambda l: reduce(lambda p, n: p*10 + n, l)
        number, position, code_string = convert(code[:3]), convert(code[3:]), str(convert(code))

        try:
            team = Team.objects.get(number=number)
            problem = Problem.objects.get(event=event, position=position)

        except Team.DoesNotExist:
            messages.add_message(self.request, messages.ERROR, 'Kód neobsahuje platný tím! Prečítané číslo tímu je {} a tento tím nie je do súťaže registrovaný. #{}'.format(number, code_string))

        except Problem.DoesNotExist:
            messages.add_message(self.request, messages.ERROR, 'Kód neobsahuje platnú úlohu! Prečítané číslo úlohy je {} a táto úloha v súťaži nie je evidovaná. #{}'.format(position, code_string))

        else:
            try:
                solution = Solution.objects.get(event=event, team=team, problem=problem)

            except Solution.DoesNotExist:
                solution = Solution.objects.create(event=event, team=team, problem=problem)
                messages.add_message(self.request, messages.SUCCESS, 'OK! Úloha {} bola úspešne odovzdaná tímom {} zo školy {}.'.format(solution.problem.position, solution.team.name, solution.team.school))

            else:
                messages.add_message(self.request, messages.ERROR, 'Táto úloha už bola odovzdaná! Stalo sa tak v čase {}. #{}'.format(solution.time, code_string))

        return super(SubmitFormView, self).form_valid(form)
    
class ResultsView(DetailView):
    model = Event
    context_object_name = 'event'

    template_name = 'competition/results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['results'] = Solution.objects.raw(results_query, [self.kwargs['pk']])

        return context
