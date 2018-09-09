from django.db import models
from django.core.validators import MinValueValidator

class Problem(models.Model):
    position = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    points = models.IntegerField()
    event = models.ForeignKey('Event', on_delete=models.CASCADE)

    def __str__(self):
        return '{}, úloha {}'.format(self.event.name, self.position)

class Solution(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    problem = models.ForeignKey('Problem', on_delete=models.CASCADE)
    team = models.ForeignKey('participant.Team', on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}, {}, úloha {}, {}'.format(self.event.name, self.team.name, self.problem.position, self.time)

class Event(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()

    team_members = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name
