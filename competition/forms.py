from csv import DictReader
from functools import reduce
from io import StringIO

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.conf import settings

from .models import (Compensation, Event, Participant, ProblemCategory,
                     Solution, Team)

# TODO: come up with slightly better control digits,
# possibly move them to settings file
CONTROL = [5, 1, 9, 3, 7]


class SubmitForm(forms.Form):
    require_control_sum = forms.BooleanField(
        label="Vyžadovať kontrolný súčet", required=False, initial=True)
    event = forms.ModelChoiceField(
        Event.objects.all(), widget=forms.HiddenInput())
    code = forms.CharField(max_length=6, label='', required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['code'].widget.attrs.update({'class': 'form-control'})

    def clean_code(self):
        require_control_sum = self.cleaned_data['require_control_sum']

        try:
            code = list(map(int, self.cleaned_data['code']))

        except ValueError as exc:
            for char in self.cleaned_data['code']:
                if char not in {"+", "ľ", "š", "č", "ť", "ž", "ý", "á", "í", "é"}:
                    raise forms.ValidationError(
                        'Nesprávny formát! Kód môže obsahovať iba číslice.') from exc
            raise forms.ValidationError(
                'Nesprávny formát! Zrejme máš nastavenú slovenskú klávesnicu, a tak miesto čísel zadávaš písmená s diakritikov. Prepni si klávesnicu na anglickú a vyskúšaj kód naskenovať ešte raz.') from exc

        if len(code) != 6 and (not require_control_sum and len(code) != 5):
            raise forms.ValidationError('Nesprávna dĺžka kódu!')

        if require_control_sum:
            checksum, code = code[-1], code[:-1]

            if checksum != reduce(lambda p, n: p + n[0]*n[1], zip(code, CONTROL), 0) % 10:
                raise forms.ValidationError('Neplatný kontrolný súčet!')

        elif len(code) == 6:
            code = code[:-1]

        return reduce(lambda p, n: p*10 + n, code)

    def clean(self):
        cleaned_data = super().clean()

        if self.errors:
            return cleaned_data

        code = cleaned_data['code']
        event = cleaned_data['event']

        number, code_position = code // 100, code % 100

        if not code_position:
            raise forms.ValidationError('Úlohy sú číslované od 1.')

        categories = ProblemCategory.objects.filter(
            event=event).order_by("position")

        position = code_position

        for category in categories:
            if position <= category.problem_count:
                break

            position -= category.problem_count

        else:
            raise forms.ValidationError(
                f'Úloha s číslom { code_position } v tejto súťaži neexistuje!')

        cleaned_data['problem_category'] = category
        cleaned_data['problem_position'] = position

        try:
            team = Team.objects.get(event=event, number=number)

        except Team.DoesNotExist as exc:
            raise forms.ValidationError(
                f'Číslo tímu { number } nezodpovedá registrovanému tímu!') from exc

        self.cleaned_data['team'] = team

        solution = Solution.objects.filter(
            team=team, problem_category=category, problem_position=position)

        if solution.exists():
            raise forms.ValidationError(
                f'Táto úloha už bola odovzdaná v čase '
                f'{ solution.first().time.strftime("%H:%M:%S (%d. %m. %Y)") }! ({ code })')

        return cleaned_data

    def save(self):
        solution = Solution.objects.create(
            team=self.cleaned_data['team'],
            problem_category=self.cleaned_data['problem_category'],
            problem_position=self.cleaned_data['problem_position'])

        return solution


class InitializeForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ('team_members', 'flat_compensation')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Vytvoriť'))

    def save(self, commit=True):
        event: Event = super().save(commit)

        event.flat_compensation = getattr(
            settings, f'{ event.name }_FLAT_COMPENSATION')
        event.team_members = getattr(settings, f'{ event.name }_TEAM_MEMBERS')
        event.save()

        compensations = getattr(settings, f'{ event.name }_COMPENSATIONS')
        problem_categories = getattr(
            settings, f'{ event.name }_PROBLEM_CATEGORIES')

        for i, category_description in enumerate(problem_categories):
            ProblemCategory.objects.create(
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


class ImportForm(forms.Form):
    event = forms.ModelChoiceField(
        queryset=Event.objects.all(), label='Vyber súťaž')

    csv_text = forms.CharField(widget=forms.Textarea, required=False, label='')
    csv_file = forms.FileField(required=False, label='')

    ignore_first_entry = forms.BooleanField(
        required=False, label='Ignorovať prvý záznam')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Nahraj'))

    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']

        if csv_file and not csv_file.name.endswith('.csv'):
            raise forms.ValidationError(
                'Nesprávna prípona súboru, akceptovaná je len CSV!')

        return csv_file

    def clean(self):
        cleaned_data = super().clean()

        if self.errors:
            return cleaned_data

        event = cleaned_data['event']
        csv_file, csv_text = cleaned_data['csv_file'], cleaned_data['csv_text']
        ignore_first_entry = cleaned_data['ignore_first_entry']

        if not (csv_file or csv_text):
            raise forms.ValidationError(
                'Súbor ani textový vstup neobsahujú žiadne dáta!')

        if csv_file and csv_text:
            raise forms.ValidationError('Vyber si len jeden zdroj údajov!')

        mapper = getattr(settings, f'{ event.name }_SCHOOL_CLASS_MAPPER')

        if not csv_text:
            csv_text = csv_file.read().decode(settings.CSV_ENCODING)

        csv_data = list(DictReader(
            StringIO(csv_text),
            fieldnames=None if ignore_first_entry else
            getattr(settings, f'{ event.name }_CSV_FIELDS'),
            delimiter=settings.CSV_DELIMITER))

        available_numbers = find_available_team_numbers(event, len(csv_data))

        if len(available_numbers) < len(csv_data):
            raise forms.ValidationError(
                'Novým tímom sa nepodarilo prideliť čísla!')

        teams_to_save, participants_to_save = [], []

        for i, row in enumerate(csv_data):
            team = Team(
                name=row['team'],
                number=available_numbers[i],
                school=row['school'],
                event=event)

            teams_to_save.append(team)

            try:
                members = int(row['members'])

            except ValueError as exc:
                raise forms.ValidationError(
                    f'Počet členov v zázname { i } nie je platné číslo') from exc

            if members > event.team_members:
                raise forms.ValidationError(
                    f'Neplatné údaje, tím  { team.name } '
                    f'má viac účastníkov ako je povolené! (záznam { i })')

            participants_to_save.append([])

            for j in range(members):
                prefix = f'participant{ j }'

                first_name = row[f'{ prefix }_first_name']
                last_name = row[f'{ prefix }_last_name']

                try:
                    school_class = mapper[row[f'{ prefix }_school_class']]

                    compensation = Compensation.objects.get(
                        event=event, school_class=school_class)

                except KeyError as exc:
                    raise forms.ValidationError(
                        f'Účastník '
                        f'{row[f"participant{j}_first_name"]} {row[f"participant{j}_last_name"]} '
                        f'zo školy {row["school"]} má neplatný ročník! (záznam {i})'
                    ) from exc
                except Compensation.DoesNotExist as exc:
                    raise forms.ValidationError(
                        f'Pre ročník {row[f"{ prefix }_school_class"]}'
                        f'({school_class}) nebola nájdená bonifikácia! (záznam {i})') from exc

                participants_to_save[i].append(Participant(
                    first_name=first_name,
                    last_name=last_name,
                    compensation=compensation))

        cleaned_data['teams_to_save'] = teams_to_save
        cleaned_data['participants_to_save'] = participants_to_save

        return cleaned_data

    def save(self):
        teams = self.cleaned_data['teams_to_save']
        participants = self.cleaned_data['participants_to_save']

        for i, team in enumerate(teams):
            team.save()

            for participant in participants[i]:
                participant.team = team
                participant.save()

        return {'teams': len(teams), 'participants': sum(len(p) for p in participants)}


def find_available_team_numbers(event, required):
    teams_in_database = Team.objects.filter(event=event).order_by('number')
    available_team_numbers = []
    pivot = 100

    # Look for numbers in between already assigned team numbers
    for team in teams_in_database:
        while pivot != team.number:
            available_team_numbers.append(pivot)
            pivot += 1

            if len(available_team_numbers) >= required:
                break

        pivot += 1

    # Look for numbers greater than already assigned numbers
    while pivot < 1000:
        available_team_numbers.append(pivot)
        pivot += 1

        if len(available_team_numbers) >= required:
            break

    return available_team_numbers
