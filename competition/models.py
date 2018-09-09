from django.db import models
from django.core.validators import MinValueValidator

class Problem(models.Model):
    position = models.IntegerField(validators=[MinValueValidator(1)])
    points = models.IntegerField()
    competition = models.ForeignKey('Competition', on_delete=models.CASCADE)

    def __str__(self):
        return '{}, úloha {}'.format(self.competition, self.position)

class Solution(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    problem = models.ForeignKey('Problem', on_delete=models.CASCADE)
    team = models.ForeignKey('participant.Team', on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}, {}, úloha {}, {}'.format(self.event, self.team, self.problem.position, self.time)

class Competition(models.Model):
    name = models.CharField(max_length=100)

    team_members = models.IntegerField(validators=[MinValueValidator(0)])

    def __str__(self):
        return self.name

class Event(models.Model):
    date = models.DateField()

    competition = models.ForeignKey('Competition', on_delete=models.CASCADE)

    def __str__(self):
        return '{} {}'.format(self.competition, self.date.year)
