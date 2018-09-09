from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView

from .models import Event, Solution, Problem
from participant.models import Team
from .forms import SubmitForm

# 5 digits, working as control sum
control = [5, 1, 9, 3, 7]

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
    template = 'competition/submit.html'

    if request.method == 'POST':
        form = SubmitForm(request.POST)

        if form.is_valid():
            try:
                barcode = form.cleaned_data['code']
            except(IndexError):
                form = SubmitForm()
                return render(request, template, {'error':True, 'form': form, 'event': event})

            if len(barcode) == 6:
                barcode = barcode[:5]
                try:
                    control_digit = int(form.cleaned_data['code'][-1])
                    control_sum = int(barcode[0])*control[0] + int(barcode[1])*control[1] + int(barcode[2])*control[2] + int(barcode[3])*control[3] + int(barcode[4])*control[4]
                except(ValueError):
                    form = SubmitForm()
                    return render(request, template, {'error':True, 'form': form, 'event': event})

                if control_digit == (control_sum % 10):
                    #team = Team.objects.get(number=int(barcode[:3]))
                    #problem = Problem.objects.get(event=event, position=int(barcode[3:5]))

                    #Solution.objects.create(event=event, problem=problem, team=team)

                    request.session['success'] = True
                    return redirect('competition:submit', pk=pk)
                else:
                    form = SubmitForm()
                    return render(request, template, {'error':True, 'form': form, 'event': event})

            else:
                form = SubmitForm()
                return render(request, template, {'error':True, 'form': form, 'event': event})
        else:
            return render(request, template, {'error':True, 'form': form, 'event': event})

    else:
        form = SubmitForm()
        try:
            success = request.session['success']
            del request.session['success']
        except:
            return render(request, template, {'form': form, 'event': event})
        else:
            return render(request, template, {'success':success, 'form': form, 'event': event})
