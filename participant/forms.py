from io import StringIO

from django import forms
from django.conf import settings
from pandas import read_csv

from competition.models import Event

from .models import Compensation, Participant, Team


class ImportForm(forms.Form):
    event = forms.ModelChoiceField(
        queryset=Event.objects.all(), label='Vyber súťaž')

    csv_text = forms.CharField(widget=forms.Textarea, required=False, label='')
    csv_file = forms.FileField(required=False, label='')

    ignore_first_entry = forms.BooleanField(
        required=False, label='Ignorovať prvý záznam')

    def __init__(self, *args, **kwargs):
        super(ImportForm, self).__init__(*args, **kwargs)
        self.fields['csv_text'].widget.attrs.update({'class': 'form-control'})
        self.fields['csv_file'].widget.attrs.update(
            {'class': 'form-control-file'})
        self.fields['event'].widget.attrs.update({'class': 'form-event'})
        self.fields['ignore_first_entry'].widget.attrs.update(
            {'class': 'form-check-input'})

    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']

        if csv_file and not csv_file.name.endswith('.csv'):
            raise forms.ValidationError(
                'Nesprávna prípona súboru, akceptovaná je len CSV!')

        return csv_file

    def clean(self):
        cleaned_data = super(ImportForm, self).clean()

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

        # TODO: choose fields and mapper based on competition type

        fields = settings.MAMUT_CSV_FIELDS
        mapper = settings.MAMUT_SCHOOL_CLASS_MAPPER

        if csv_file:
            dataframe = read_csv(
                csv_file,
                names=fields,
                delimiter=settings.CSV_DELIMITER,
                encoding=settings.CSV_ENCODING,
            )

        else:
            dataframe = read_csv(
                StringIO(csv_text),
                names=fields,
                delimiter=settings.CSV_DELIMITER,
            )

        if ignore_first_entry:
            dataframe.drop(dataframe.index[0], inplace=True)

        available_numbers = find_available_team_numbers(event, len(dataframe))

        # In case there's not enough available numbers
        if len(available_numbers) < len(dataframe):
            raise forms.ValidationError(
                'Novým tímom sa nepodarilo prideliť čísla!')

        teams_to_save, participants_to_save = [], []

        for i, row in dataframe.iterrows():
            if ignore_first_entry:
                i -= 1

            team = Team(
                name=row['team'],
                number=available_numbers[i],
                school=row['school'],
                event=event
            )

            teams_to_save.append(team)

            if int(row['members']) > event.team_members:
                raise forms.ValidationError(
                    'Neplatné údaje, tím {} má viac účastníkov ako je povolené! (záznam {})'.format(
                        team.name, i))

            participants_to_save.append([])

            for j in range(int(row['members'])):
                prefix = 'participant{}'.format(j)

                first_name = row['{}_first_name'.format(prefix)]
                last_name = row['{}_last_name'.format(prefix)]

                try:
                    school_class = mapper[
                        row['{}_school_class'.format(prefix)]]

                    compensation = Compensation.objects.get(
                        event=event, school_class=school_class)

                except KeyError:
                    raise forms.ValidationError(
                        'Účastník {} {} zo školy {} má neplatný ročník! (záznam {})'.format(
                            row['participant{}_first_name'.format(j)],
                            row['participant{}_last_name'.format(j)],
                            row['school'], i))

                except Compensation.DoesNotExist:
                    raise forms.ValidationError(
                        'Pre ročník {} ({}) nebola nájdená bonifikácia! (záznam {})'.format(
                            row['{}_school_class'].format(prefix), school_class, i))

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

        return {'teams': len(teams), 'participants': sum([len(p) for p in participants])}


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
