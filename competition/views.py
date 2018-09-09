from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView

from .models import Event, Solution, Problem
from participant.models import Team
from .forms import SubmitForm

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

    if request.method == 'POST':
        form = SubmitForm(request.POST)

        if form.is_valid():
            team = Team.objects.get(pk=int(form.cleaned_data['code'][:3]))
            problem = Problem.objects.get(event=event, position=int(form.cleaned_data['code'][3:]))

            Solution.objects.create(event=event, problem=problem, team=team)

            return redirect('competition:submit', pk=pk)

    else:
        form = SubmitForm()

    return render(request, 'competition/submit.html', {'form': form, 'event': event})
