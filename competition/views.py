from functools import reduce

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
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
    event = get_object_or_404(Event, pk=pk)
    template_name = 'competition/submit.html'

    if request.method == 'POST':
        form = SubmitForm(request.POST)

        if form.is_valid():
            code = form.cleaned_data['code']

            convert = lambda l: reduce(lambda p, n: p*10 + n, l)
            number, position, code_string = convert(code[:3]), convert(code[3:]), str(convert(code))

            try:
                team = Team.objects.get(number=number)
                problem = Problem.objects.get(event=event, position=position)

            except Team.DoesNotExist:
                messages.add_message(request, messages.ERROR, 'Kód neobsahuje platný tím! Prečítané číslo tímu je {} a tento tím nie je do súťaže registrovaný. #{}'.format(number, code_string))

            except Problem.DoesNotExist:
                messages.add_message(request, messages.ERROR, 'Kód neobsahuje platnú úlohu! Prečítané číslo úlohy je {} a táto úloha v súťaži nie je evidovaná. #{}'.format(position, code_string))

            else:
                try:
                    solution = Solution.objects.get(event=event, team=team, problem=problem)

                except Solution.DoesNotExist:
                    solution = Solution.objects.create(event=event, team=team, problem=problem)
                    messages.add_message(request, messages.SUCCESS, 'OK! Úloha {} bola úspešne odovzdaná tímom zo školy {}.'.format(solution.problem.position, solution.team.school.name))
                    form = SubmitForm()

                    return redirect('competition:submit')

                else:
                    messages.add_message(request, messages.ERROR, 'Táto úloha už bola odovzdaná! Stalo sa tak v čase {}. #{}'.format(solution.time, code_string))

    else:
        form = SubmitForm()

    return render(request, template_name, {'form': form, 'event': event})

def results(request, pk):
    event = get_object_or_404(Event, pk=pk)
    template_name = 'competition/results.html'

    results = Solution.objects.raw('''
    SELECT
        participant_team.id AS id,
        participant_team.name AS team_name,
        participant_school.name AS school_name,
        participant_school.address AS school_address,
        participant_school.city AS school_city,
        members.members AS team_members,
        SUM(competition_problem.points) AS points,
        hardest_position.position AS hardest_position,
        hardest_time.time AS hardest_time
    FROM competition_solution
    JOIN participant_team ON competition_solution.team_id = participant_team.id
    JOIN competition_problem ON competition_solution.problem_id = competition_problem.id
    JOIN participant_school ON participant_team.school_id = participant_school.id
    LEFT OUTER JOIN (
        SELECT
            GROUP_CONCAT(participants.full_name, ", ") AS members,
            participants.team_id
        FROM (
            SELECT
                participant_participant.first_name || " " || participant_participant.last_name AS full_name,
                participant_participant.team_id
            FROM
                participant_participant
        ) AS participants
        GROUP BY participants.team_id
    ) AS members ON competition_solution.team_id = members.team_id
    JOIN (
        SELECT
            MAX(competition_problem.position) AS position,
            competition_solution.team_id
        FROM competition_solution
        JOIN competition_problem ON competition_solution.problem_id = competition_problem.id
        GROUP BY competition_solution.team_id
    ) AS hardest_position ON competition_solution.team_id = hardest_position.team_id
    JOIN  (
        SELECT
            competition_solution.time AS time,
            competition_solution.team_id
        FROM competition_solution
        JOIN competition_problem ON competition_solution.problem_id = competition_problem.id
        GROUP BY competition_solution.team_id
        HAVING competition_problem.position = MAX(competition_problem.position)
    ) AS hardest_time ON competition_solution.team_id = hardest_time.team_id
    WHERE competition_solution.event_id = %s
    GROUP BY competition_solution.team_id
    ORDER BY
        points DESC,
        hardest_position DESC,
        hardest_time ASC
    ''', [pk])

    return render(request, template_name, {'event': event, 'results': results})
