from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Problem(models.Model):
    position = models.SmallIntegerField()
    points = models.SmallIntegerField()
    event = models.ForeignKey('Event', on_delete=models.CASCADE)

    def __str__(self):
        return '{}, úloha {}'.format(self.event, self.position)


class Solution(models.Model):
    problem = models.ForeignKey('Problem', on_delete=models.CASCADE)
    team = models.ForeignKey('participant.Team', on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}, {}, úloha {}, {}'.format(self.team.event, self.team.name, self.problem.position, self.time)


class Event(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()

    team_members = models.PositiveSmallIntegerField()

    def __str__(self):
        return '{} {}'.format(self.name, self.date.year)


class Compensation(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    school_class = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(9)])
    points = models.SmallIntegerField()

    def __str__(self):
        return 'Bonifikácia {}, {}. ročník'.format(self.event, self.school_class)
