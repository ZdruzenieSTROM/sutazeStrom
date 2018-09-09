from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Team(models.Model):
    name = models.CharField(max_length=200)

    school = models.ForeignKey('School', on_delete=models.CASCADE)

    event = models.ForeignKey('competition.Event', on_delete=models.CASCADE)

    def __str__(self):
        return '{}, {}'.format(self.name, self.school.name)

class Participant(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    team = models.ForeignKey('Team', on_delete=models.CASCADE)

    school_class = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(9)])

    def __str__(self):
        return '{} {}, {}'.format(self.first_name, self.last_name, self.team.school.name)

class School(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200, help_text='Ulica s číslom')
    city = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=6)

    def __str__(self):
        return '{}, {}, {} {}'.format(self.name, self.address, self.postal_code, self.city)
