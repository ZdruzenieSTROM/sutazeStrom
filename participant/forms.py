from io import StringIO

from django import forms
from django.conf import settings
from pandas import read_csv

from competition.models import Event

from .models import Compensation, Participant, Team

CSV_FIELDS = [
    'tim',
    'skola',
    'ico',
    'pocet_clenov',
    'kontakt_meno',
    'kontakt_email',
    'kontakt_tel',
    'ucastnik1_meno',
    'ucastnik1_priezvisko',
    'ucastnik1_rocnik',
    'ucastnik1_email',
    'ucastnik1_a1',
    'ucastnik1_a2',
    'ucastnik1_a3',
    'ucastnik2_meno',
    'ucastnik2_priezvisko',
    'ucastnik2_rocnik',
    'ucastnik2_email',
    'ucastnik2_a1',
    'ucastnik2_a2',
    'ucastnik2_a3',
    'ucastnik3_meno',
    'ucastnik3_priezvisko',
    'ucastnik3_rocnik',
    'ucastnik3_email',
    'ucastnik3_a1',
    'ucastnik3_a2',
    'ucastnik3_a3',
    'ucastnik4_meno',
    'ucastnik4_priezvisko',
    'ucastnik4_rocnik',
    'ucastnik4_email',
    'ucastnik4_a1',
    'ucastnik4_a2',
    'ucastnik4_a3',
    'cislo_timu',
]

ROCNIKY = {
    'prvý': 1,
    'druhý': 2,
    'tretí': 3,
    'štvrtý': 4,
    'piaty': 5,
    'šiesty': 6,
    'príma': 6,
    'siedmy': 7,
    'sekunda': 7,
    'ôsmy': 8,
    'tercia': 8,
    'deviaty': 9,
    'kvarta': 9,
}


class ImportForm(forms.Form):
    event = forms.ModelChoiceField(
        queryset=Event.objects.all(), label='Vyber súťaž')

    csv_text = forms.CharField(widget=forms.Textarea, required=False, label='')
    csv_file = forms.FileField(required=False, label='')

    def __init__(self, *args, **kwargs):
        super(ImportForm, self).__init__(*args, **kwargs)
        self.fields['csv_text'].widget.attrs.update({'class': 'form-control'})
        self.fields['csv_file'].widget.attrs.update(
            {'class': 'form-control-file'})
        self.fields['event'].widget.attrs.update({'class': 'form-event'})

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

        if not (csv_file or csv_text):
            raise forms.ValidationError(
                'Súbor ani textový vstup neobsahujú žiadne dáta!')

        if csv_file and csv_text:
            raise forms.ValidationError('Vyber si len jeden zdroj údajov!')

        if csv_file:
            dataframe = read_csv(
                csv_file,
                names=CSV_FIELDS,
                delimiter=settings.CSV_DELIMITER,
                encoding=settings.CSV_ENCODING,
            )

        else:
            dataframe = read_csv(
                StringIO(csv_text),
                names=CSV_FIELDS,
                delimiter=settings.CSV_DELIMITER,
            )

        teams_to_import = dataframe['tim']
        schools_to_import = dataframe['skola']
        participant_counts = dataframe['pocet_clenov']

        try:
            participants_to_import = [
                {
                    'first_names': dataframe['ucastnik{}_meno'.format(i)],
                    'last_names': dataframe['ucastnik{}_priezvisko'.format(i)],
                    'school_classes': dataframe['ucastnik{}_rocnik'.format(i)]
                } for i in range(1, event.team_members + 1)
            ]

        except KeyError:
            raise forms.ValidationError(
                'Niektorý zo záznamov nemá dostatočný počet stĺpcov s účastníkmi!')

        available_team_numbers = self.find_available_team_numbers(
            event, len(teams_to_import) - 1)

        # In case there's not enough available numbers
        if len(available_team_numbers) < len(teams_to_import) - 1:
            raise forms.ValidationError(
                'Novým tímom sa nepodarilo prideliť čísla!')

        teams_to_save, participants_to_save = [], []

        for i, _ in enumerate(teams_to_import[1:], 1):
            team = Team(
                name=teams_to_import[i],
                number=available_team_numbers[i-1],
                school=schools_to_import[i],
                event=event
            )

            teams_to_save.append(team)

            if int(participant_counts[i]) > event.team_members:
                raise forms.ValidationError(
                    'Neplatné údaje, tím {} má viac tímov ako je povolené! (záznam {})'.format(
                        team.name, i))

            participants_to_save.append([])

            for j in range(int(participant_counts[i])):
                try:
                    school_class = ROCNIKY[participants_to_import[j]
                                           ['school_classes'][i]]

                except KeyError:
                    raise forms.ValidationError(
                        'Účastník {} {} zo školy {} má neplatný ročník! (záznam {})'.format(
                            participants_to_import[j]['first_names'][i],
                            participants_to_import[j]['last_names'][i],
                            schools_to_import[i], i
                        ))

                try:
                    compensation = Compensation.objects.get(
                        event=event, school_class=school_class)

                except Compensation.DoesNotExist:
                    raise forms.ValidationError(
                        'Pre ročník {} ({}) nebola nájdená bonifikácia! (záznam {})'.format(
                            participants_to_import[j]['school_classes'][i], school_class, i))

                participants_to_save[i-1].append(Participant(
                    first_name=participants_to_import[j]['first_names'][i],
                    last_name=participants_to_import[j]['last_names'][i],
                    team=team,
                    compensation=compensation
                ))

        cleaned_data['teams_to_save'] = teams_to_save
        cleaned_data['participants_to_save'] = participants_to_save

        return cleaned_data

    def find_available_team_numbers(self, event, required):
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

    def save(self):
        teams = self.cleaned_data['teams_to_save']
        participants = self.cleaned_data['participants_to_save']

        for i, team in enumerate(teams):
            team.save()

            for participant in participants[i]:
                participant.team = team
                participant.save()

        return {'saved_teams': len(teams), 'saved_participants': sum([len(p) for p in participants])}
