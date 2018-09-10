from functools import reduce

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic import DetailView, ListView

from participant.models import Team

from .forms import SubmitForm
from .models import Event, Problem, Solution


class EventListView(ListView):
    model = Event
    template_name = 'competition/index.html'
    context_object_name = 'events'

class EventDetailView(DetailView):
    model = Event
    template_name = 'competition/event.html'
    context_object_name = 'event'

def submit(request, pk):
    event = Event.objects.get(pk=pk)
    template_name = 'competition/submit.html'

    if request.method == 'POST':
        form = SubmitForm(request.POST)

        if form.is_valid():
            code = form.cleaned_data['code']

            convert = lambda l: reduce(lambda p, n: p*10 + n, l)
            number, position = convert(code[:3]), convert(code[3:])

            try:
                team = Team.objects.get(number=number)
                problem = Problem.objects.get( event=event, position=position)

            except Team.DoesNotExist:
                messages.add_message(request, messages.ERROR, 'Kód neobsahuje platný tím')

            except Problem.DoesNotExist:
                messages.add_message(request, messages.ERROR, 'Kód neobsahuje platnú úlohu')

            else:
                try:
                    Solution.objects.get(event=event, team=team, problem=problem)

                except Solution.DoesNotExist:
                    Solution.objects.create(event=event, team=team, problem=problem)
                    messages.add_message(request, messages.SUCCESS, 'Úloha bola úspešne odovzdaná')
                    form = SubmitForm()

                else:
                    messages.add_message(request, messages.ERROR, 'Táto úloha už bola odovzdaná')

    else:
        form = SubmitForm()

    return render(request, template_name, {'form': form, 'event': event})
