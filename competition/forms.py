from functools import reduce

from django import forms
from django.conf import settings

from participant.models import Compensation, Team

from .models import Event, ProblemCategory, Solution

CONTROL = [5, 1, 9, 3, 7]


class SubmitForm(forms.Form):
    require_control_sum = forms.BooleanField(
        label="Vyžadovať kontrolný súčet", required=False, initial=True)
    event = forms.ModelChoiceField(
        Event.objects.all(), widget=forms.HiddenInput())
    code = forms.CharField(max_length=6, label='', required=True)

    def __init__(self, *args, **kwargs):
        super(SubmitForm, self).__init__(*args, **kwargs)
        self.fields['code'].widget.attrs.update({'class': 'form-control'})

    def clean_code(self):
        require_control_sum = self.cleaned_data['require_control_sum']

        try:
            code = list(map(int, self.cleaned_data['code']))

        except ValueError:
            raise forms.ValidationError('Nesprávny formát!')

        if (len(code) != 6 and require_control_sum) or (len(code) != 5 and not require_control_sum):
            raise forms.ValidationError('Nesprávna dĺžka kódu!')

        if require_control_sum:
            checksum, code = code[-1], code[:-1]

            if checksum != reduce(lambda p, n: p + n[0]*n[1], zip(code, CONTROL), 0) % 10:
                raise forms.ValidationError('Neplatný kontrolný súčet!')

        return reduce(lambda p, n: p*10 + n, code)

    def clean(self):
        cleaned_data = super(SubmitForm, self).clean()

        if not self.errors:
            code = cleaned_data['code']
            event = cleaned_data['event']

            number, code_position = code // 100, code % 100

            if code_position == 0:
                raise forms.ValidationError(
                    'Úloha s číslom {} v tejto súťaži neexistuje!'.format(code_position))

            categories = ProblemCategory.objects.filter(
                event=event).order_by("position")

            position = code_position

            for category in categories:
                if position <= category.problem_count:
                    break

                position -= category.problem_count

            else:
                raise forms.ValidationError(
                    'Úloha s číslom {} v tejto súťaži neexistuje!'.format(code_position))

            cleaned_data['problem_category'] = category
            cleaned_data['problem_position'] = position

            try:
                team = Team.objects.get(event=event, number=number)

            except Team.DoesNotExist:
                raise forms.ValidationError(
                    'Číslo tímu {} nezodpovedá registrovanému tímu!'.format(
                        number))

            self.cleaned_data['team'] = team

            solution = Solution.objects.filter(
                team=team, problem_category=category, problem_position=position)

            if solution.exists():
                raise forms.ValidationError(
                    'Táto úloha už bola odovzdaná v čase {}! ({})'.format(
                        solution.first().time.strftime('%H:%M:%S (%d. %m. %Y)'), code))

        return cleaned_data

    def save(self):
        solution = Solution.objects.create(
            team=self.cleaned_data['team'],
            problem_category=self.cleaned_data['problem_category'],
            problem_position=self.cleaned_data['problem_position'])

        return solution


class InitializeCompetitionForm(forms.Form):
    competition = forms.ChoiceField(
        choices=(('LOMIHLAV', 'Lomihlav'), ('MAMUT', 'Mamut')))
    date = forms.DateField(label='Dátum konania',
                           help_text='Formát: rrrr-mm-dd')

    def __init__(self, *args, **kwargs):
        super(InitializeCompetitionForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget.attrs.update({'class': 'form-control'})

    def save(self):
        competition = self.cleaned_data['competition']
        date = self.cleaned_data['date']

        if competition == 'LOMIHLAV':
            name = 'Lomihlav'
            flat_compensation = False
        else:
            name = 'Mamut'
            flat_compensation = True

        members = getattr(settings, '{}_TEAM_MEMBERS'.format(competition))
        school_class_mapper = getattr(
            settings, '{}_SCHOOL_CLASS_MAPPER'.format(competition))
        problem_categories = getattr(
            settings, '{}_PROBLEM_CATEGORIES'.format(competition))
        compensations = getattr(
            settings, '{}_COMPENSATIONS'.format(competition))

        event = Event.objects.create(
            name=name, date=date,
            team_members=members,
            flat_compensation=flat_compensation)

        for i, category_description in enumerate(problem_categories):
            category = ProblemCategory.objects.create(
                name=category_description['name'],
                event=event, position=i,
                points=category_description['points'],
                problem_count=category_description['count'],
                multiplicative_compensation=category_description['mcomp'],
                is_problem=category_description['is_problem'])

        for compensation_description in compensations:
            Compensation.objects.create(
                event=event,
                points=compensation_description['points'],
                school_class=compensation_description['class'])

        return event
