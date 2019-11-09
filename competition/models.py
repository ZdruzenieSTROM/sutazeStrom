from django.db import models


class Event(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()

    team_members = models.PositiveSmallIntegerField()
    flat_compensation = models.BooleanField()

    def __str__(self):
        return '{} {}'.format(self.name, self.date.year)


class ProblemCategory(models.Model):
    name = models.CharField(max_length=100)
    event = models.ForeignKey('Event', on_delete=models.CASCADE)

    position = models.SmallIntegerField()
    problem_count = models.PositiveSmallIntegerField()
    points = models.DecimalField(max_digits=6, decimal_places=2)
    multiplicative_compensation = models.BooleanField()
    is_problem = models.BooleanField()

    class Meta:
        verbose_name_plural = 'problem categories'

    def __str__(self):
        return '{}, {}'.format(self.event, self.name)


class Solution(models.Model):
    problem_category = models.ForeignKey(
        'ProblemCategory', on_delete=models.CASCADE)
    problem_position = models.PositiveSmallIntegerField()
    team = models.ForeignKey('participant.Team', on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}, {}, úloha {} - {}, {}'.format(
            self.team.event, self.team.name,
            self.problem_category.name,
            self.problem_position, self.time)
