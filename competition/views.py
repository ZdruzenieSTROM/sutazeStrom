from django.contrib import messages
from django.shortcuts import reverse
from django.views.generic import DetailView, FormView, ListView
from django.views.generic.detail import SingleObjectMixin

from .forms import SubmitForm
from .models import Event, Solution
from .queries import RESULTS_QUERY


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

        context['solutions'] = Solution.objects.filter(team__event=self.object).order_by('-time')[:10]

        return context

    def form_valid(self, form):
        solution = form.save()

        messages.add_message(self.request, messages.SUCCESS,\
                             'Úloha {} bola úspešne odovzdaná tímom {} zo školy {}.'.format(\
                             solution.problem.position, solution.team.name, solution.team.school))

        return super(SubmitFormView, self).form_valid(form)

class ResultsView(DetailView):
    model = Event
    context_object_name = 'event'

    template_name = 'competition/results.html'

    def get_context_data(self, **kwargs):
        context = super(ResultsView, self).get_context_data(**kwargs)
        context['results'] = Solution.objects.raw(RESULTS_QUERY, [self.kwargs['pk']])

        return context
