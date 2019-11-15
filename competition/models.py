from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Event(models.Model):
    EVENT_NAME_CHOICES = (
        ('LOMIHLAV', 'Lomihlav'),
        ('MAMUT', 'Mamut'),
    )

    name = models.CharField(max_length=100, choices=EVENT_NAME_CHOICES)
    date = models.DateField()

    team_members = models.PositiveSmallIntegerField(null=True)
    flat_compensation = models.BooleanField(null=True)

    def __str__(self):
        return f'{ self.get_name_display() } { self.date.year }'


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
    team = models.ForeignKey('Team', on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}, {}, úloha {} - {}, {}'.format(
            self.team.event, self.team.name,
            self.problem_category.name,
            self.problem_position, self.time)


class Team(models.Model):
    name = models.CharField(max_length=200)
    number = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(100), MaxValueValidator(999)])

    school = models.CharField(max_length=300)

    event = models.ForeignKey('Event', on_delete=models.CASCADE)

    def __str__(self):
        return '{}, {}'.format(self.name, self.school)


class Participant(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    team = models.ForeignKey('Team', on_delete=models.CASCADE)

    compensation = models.ForeignKey('Compensation', on_delete=models.CASCADE)

    def __str__(self):
        return '{} {}, {}'.format(self.first_name, self.last_name, self.team.school)


class Compensation(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    points = models.DecimalField(max_digits=6, decimal_places=2)

    school_class = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(9)])

    def __str__(self):
        return 'Bonifikácia {}, {}. ročník'.format(self.event, self.school_class)
