from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Event(models.Model):
    EVENT_NAME_CHOICES = (
        ('LOMIHLAV', 'Lomihlav'),
        ('MAMUT', 'Mamut'),
    )

    name = models.CharField(
        max_length=100, choices=EVENT_NAME_CHOICES, verbose_name='Názov')
    date = models.DateField(verbose_name='Dátum konania',
                            help_text='Formát: RRRR-MM-DD')

    frozen_results = models.TextField(
        null=True, blank=True, verbose_name='Zmrznutá výsledkovka')
    team_members = models.PositiveSmallIntegerField(null=True)
    flat_compensation = models.BooleanField(null=True)
    length = models.DurationField(verbose_name='Trvanie súťaže')
    started_at = models.DateTimeField(null=True, blank=True)

    def end_time(self):
        if self.started_at is None:
            return None
        return self.started_at + self.length

    def __str__(self):
        return f'{ self.get_name_display() } { self.date.year }'
    
    def save(self, *args, **kwargs):
        if not self.frozen_results:
            self.frozen_results = None
        super().save(*args, **kwargs)


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
        return f'{ self.event }, { self.name }'


class Solution(models.Model):
    problem_category = models.ForeignKey(
        'ProblemCategory', on_delete=models.CASCADE)
    problem_position = models.PositiveSmallIntegerField()
    team = models.ForeignKey('Team', on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{ self.team.event }, { self.team.name }, '\
            f'úloha { self.problem_category.name } - { self.problem_position }, { self.time }'


class Team(models.Model):
    name = models.CharField(max_length=200)
    number = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(100), MaxValueValidator(999)])

    school = models.CharField(max_length=300)

    event = models.ForeignKey('Event', on_delete=models.CASCADE)

    def __str__(self):
        return f'{ self.name }, { self.school }'


class Participant(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    team = models.ForeignKey('Team', on_delete=models.CASCADE)

    compensation = models.ForeignKey('Compensation', on_delete=models.CASCADE)

    def __str__(self):
        return f'{ self.first_name } { self.last_name }, { self.team.school }'


class Compensation(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    points = models.DecimalField(max_digits=6, decimal_places=2)

    school_class = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(9)])

    def __str__(self):
        return f'Bonifikácia { self.event }, { self.school_class }. ročník'
