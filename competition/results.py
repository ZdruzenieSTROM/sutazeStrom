
import datetime
from decimal import Decimal
from operator import itemgetter
from typing import Any

from django.db.models import Sum
from django.db.models.manager import BaseManager

from .models import Event, ProblemCategory, Solution, Team


def get_latest_solution_or_none(team: Team, event: Event) -> datetime.datetime | None:
    try:
        if event.end_time() is None:
            return None
        return event.end_time() - team.solution_set.latest().time
    except Solution.DoesNotExist:
        return None


def build_team_dict(team: Team, event: Event, categories: BaseManager[ProblemCategory]) -> dict[str, Any]:
    return {
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
        'spare_time': get_latest_solution_or_none(team, event)
    }


def compute_points(team: dict, event: Event, categories: BaseManager[ProblemCategory]):
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


def get_sort_criteria(event_name: str):
    match event_name:
        case 'LOMIHLAV':
            return itemgetter('total_points', 'solved_problems')
        case 'MAMUT':
            return itemgetter(
                'total_points', 'problem_points', 'solved_problems', 'spare_time')
        case _:
            raise NotImplementedError(
                f'Competition with name {event_name} is not supported')


def add_ranks(teams: list[dict], sort_criteria):
    def save_team_ranks(teams: list, lower_rank: int):
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
                sort_criteria(team) == sort_criteria(identically_ranked_teams[-1]):
            identically_ranked_teams.append(team)
        else:
            lower_rank = save_team_ranks(
                identically_ranked_teams, lower_rank) + 1

            identically_ranked_teams.clear()
            identically_ranked_teams.append(team)

    save_team_ranks(identically_ranked_teams, lower_rank)


def generate_results(event: Event):
    categories = ProblemCategory.objects.filter(
        event=event).order_by('position')

    # Pull information about teams from database
    # TODO: use annotate instead of pulling data into a dictionary
    teams = [
        build_team_dict(team, event, categories)
        for team in Team.objects.filter(event=event)
    ]

    # Compute points
    for team in teams:
        compute_points(team, event, categories)

    # Sort teams
    sort_criteria = get_sort_criteria(event.name)
    teams.sort(key=sort_criteria, reverse=True)

    # Generate ranks
    add_ranks(teams, sort_criteria)

    return (categories, teams)
