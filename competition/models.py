from django.db import models


class Event(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()

    team_members = models.PositiveSmallIntegerField()

    def __str__(self):
        return '{} {}'.format(self.name, self.date.year)


class Problem(models.Model):
    position = models.SmallIntegerField()
    category = models.ForeignKey('ProblemCategory', on_delete=models.CASCADE)

    def __str__(self):
        return '{}, úloha {}'.format(self.category, self.position)


class ProblemCategory(models.Model):
    name = models.CharField(max_length=100)
    event = models.ForeignKey('Event', on_delete=models.CASCADE)

    position = models.SmallIntegerField()
    points = models.SmallIntegerField()

    class Meta:
        verbose_name_plural = 'problem categories'

    def __str__(self):
        return '{}, {} úlohy'.format(self.event, self.name)


class Solution(models.Model):
    problem = models.ForeignKey('Problem', on_delete=models.CASCADE)
    team = models.ForeignKey('participant.Team', on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}, {}, úloha {}, {}'.format(
            self.team.event,
            self.team.name,
            self.problem.position,
            self.time
        )
