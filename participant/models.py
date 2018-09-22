from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

class Team(models.Model):
    name = models.CharField(max_length=200)
    number = models.PositiveSmallIntegerField(unique=True, validators=[MinValueValidator(100), MaxValueValidator(999)])

    school = models.CharField(max_length=300)

    event = models.ForeignKey('competition.Event', on_delete=models.CASCADE)

    def __str__(self):
        return '{}, {}'.format(self.name, self.school)

class Participant(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    team = models.ForeignKey('Team', on_delete=models.CASCADE)

    school_class = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(9)])

    def __str__(self):
        return '{} {}, {}'.format(self.first_name, self.last_name, self.team.school)
