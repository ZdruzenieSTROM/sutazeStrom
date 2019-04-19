from functools import reduce

from django import forms
from django.conf import settings

from participant.models import Compensation, Team

from .models import Event, Problem, ProblemCategory, Solution

CONTROL = [5, 1, 9, 3, 7]


class SubmitForm(forms.Form):
    event = forms.ModelChoiceField(
        Event.objects.all(), widget=forms.HiddenInput())
    code = forms.CharField(max_length=6, label='', required=True)

    def __init__(self, *args, **kwargs):
        super(SubmitForm, self).__init__(*args, **kwargs)
        self.fields['code'].widget.attrs.update({'class': 'form-control'})

    def clean_code(self):
        try:
            code = [int(c) for c in self.cleaned_data['code']]

        except ValueError:
            raise forms.ValidationError('Nesprávny formát!')

        if len(code) != 6:
            raise forms.ValidationError('Nesprávna dĺžka kódu!')

        control_digit, code = code[-1], code[:-1]

        if control_digit != reduce(lambda p, n: p + n[0]*n[1], zip(code, CONTROL), 0) % 10:
            raise forms.ValidationError('Neplatný kontrolný súčet!')

        return reduce(lambda p, n: p*10 + n, code)

    def clean(self):
        cleaned_data = super(SubmitForm, self).clean()

        if not self.errors:
            code = cleaned_data['code']
            event = cleaned_data['event']

            number, position = code // 100, code % 100

            categories = ProblemCategory.objects.filter(event=event).order_by("position")
            pcategory = None

            for category in categories:
                if position > category.problem_set.count():
                    position -= category.problem_set.count()
                else:
                    pcategory = category

            try:
                team = Team.objects.get(event=event, number=number)
                problem = Problem.objects.get(
                    category__event=event, position=position, category=pcategory)

            except Team.DoesNotExist:
                raise forms.ValidationError(
                    'Číslo tímu {} nezodpovedá registrovanému tímu!'.format(
                        number)
                )

            except Problem.DoesNotExist:
                raise forms.ValidationError(
                    'Úloha číslo {} v tejto súťaži neexistuje!'.format(
                        position)
                )

            else:
                self.cleaned_data['team'] = team
                self.cleaned_data['problem'] = problem

                try:
                    solution = Solution.objects.get(team=team, problem=problem)

                except Solution.DoesNotExist:
                    pass

                else:
                    raise forms.ValidationError(
                        'Táto úloha už bola odovzdaná v čase {}! ({})'.format(
                            solution.time.strftime('%H:%M:%S (%d. %m. %Y)'),
                            code
                        )
                    )

        return cleaned_data

    def save(self):
        solution = Solution.objects.create(
            team=self.cleaned_data['team'],
            problem=self.cleaned_data['problem']
        )

        return solution


class InitializeMamutForm(forms.Form):
    date = forms.DateField(label='Dátum konania',
                           help_text='Formát: rrrr-mm-dd')

    def __init__(self, *args, **kwargs):
        super(InitializeMamutForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget.attrs.update({'class': 'form-control'})

    def save(self):
        date = self.cleaned_data['date']

        event = Event.objects.create(
            name='Mamut',
            date=date,
            team_members=settings.MAMUT_TEAM_MEMBERS
        )

        for i, category_description in enumerate(settings.MAMUT_PROBLEM_CATEGORIES):
            category = ProblemCategory.objects.create(
                name=category_description['name'],
                event=event,
                position=i,
                points=category_description['points']
            )

            for j in range(1, category_description['count'] + 1):
                Problem.objects.create(position=j, category=category)

        for compensation_description in settings.MAMUT_COMPENSATIONS:
            Compensation.objects.create(
                event=event,
                points=compensation_description['points'],
                school_class=compensation_description['class']
            )

        return event
