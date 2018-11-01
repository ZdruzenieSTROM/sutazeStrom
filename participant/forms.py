from io import StringIO

from django import forms
from django.conf import settings
from pandas import read_csv

from competition.models import Event
from .models import *

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

ROCNIK_1 = [
    'prvý',
]

ROCNIK_2 = [
    'druhý',
]

ROCNIK_3 = [
    'tretí',
]

ROCNIK_4 = [
    'štvrtý',
]

ROCNIK_5 = [
    'piaty',
]

ROCNIK_6 = [
    'šiesty',
    'príma',
]

ROCNIK_7 = [
    'siedmy',
    'sekunda',
]

ROCNIK_8 = [
    'ôsmy',
    'tercia',
]

ROCNIK_9 = [
    'deviaty',
    'kvarta',
]

def resolve_class(name):
    name = str(name)
    if name in ROCNIK_1:
        return 1
    elif name in ROCNIK_2:
        return 2
    elif name in ROCNIK_3:
        return 3
    elif name in ROCNIK_4:
        return 4
    elif name in ROCNIK_5:
        return 5
    elif name in ROCNIK_6:
        return 6
    elif name in ROCNIK_7:
        return 7
    elif name in ROCNIK_8:
        return 8
    elif name in ROCNIK_9:
        return 9
    else:
        return None

def new_number():
    found = False
    x = 100
    existing = []
    for team in Team.objects.all():
        existing.append(team.number)

    while not found:
        if x in existing:
            x += 1
        else:
            found = True
            return x


class ImportForm(forms.Form):
    event = forms.ModelChoiceField(queryset=Event.objects.all(), label='Vyber súťaž')

    csv_text = forms.CharField(widget=forms.Textarea, required=False, label='')
    csv_file = forms.FileField(required=False, label='')

    def __init__(self, *args, **kwargs):
        super(ImportForm, self).__init__(*args, **kwargs)
        self.fields['csv_text'].widget.attrs.update({'class': 'form-control'})
        self.fields['csv_file'].widget.attrs.update({'class': 'form-control-file'})
        self.fields['event'].widget.attrs.update({'class': 'form-event'})

    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']

        if csv_file and not csv_file.name.endswith('.csv'):
            raise forms.ValidationError('Nesprávna prípona súboru, akceptovaná je len CSV!')

        return csv_file

    def clean(self):
        cleaned_data = super(ImportForm, self).clean()

        if not self.errors:
            csv_file, csv_text = cleaned_data['csv_file'], cleaned_data['csv_text']
            event = cleaned_data['event']

            if not (csv_file or csv_text):
                raise forms.ValidationError('Súbor ani textový vstup neobsahujú žiadne dáta!')

            if not event:
                raise forms.ValidationError('Vyber event!')

            if csv_file and csv_text:
                raise forms.ValidationError('Vyber si len jeden zdroj údajov!')

            if csv_file:
                self.cleaned_data['dataframe'] = read_csv(
                    csv_file,
                    names=CSV_FIELDS,
                    delimiter=settings.CSV_DELIMITER,
                    encoding=settings.CSV_ENCODING,
                )
            else:
                self.cleaned_data['dataframe'] = read_csv(
                    StringIO(csv_text),
                    names=CSV_FIELDS,
                    delimiter=settings.CSV_DELIMITER,
                )

        return cleaned_data

    'ucastnik1_meno'
    'ucastnik1_priezvisko'
    'ucastnik1_rocnik'

    def save(self):
        event = self.cleaned_data['event']
        teams = self.cleaned_data['dataframe']['tim']
        schools = self.cleaned_data['dataframe']['skola']
        participants = self.cleaned_data['dataframe']['pocet_clenov']

        u1_names = self.cleaned_data['dataframe']['ucastnik1_meno']
        u1_surnames = self.cleaned_data['dataframe']['ucastnik1_priezvisko']
        u1_classes = self.cleaned_data['dataframe']['ucastnik1_rocnik']

        u2_names = self.cleaned_data['dataframe']['ucastnik1_meno']
        u2_surnames = self.cleaned_data['dataframe']['ucastnik1_priezvisko']
        u2_classes = self.cleaned_data['dataframe']['ucastnik1_rocnik']

        u3_names = self.cleaned_data['dataframe']['ucastnik1_meno']
        u3_surnames = self.cleaned_data['dataframe']['ucastnik1_priezvisko']
        u3_classes = self.cleaned_data['dataframe']['ucastnik1_rocnik']

        u4_names = self.cleaned_data['dataframe']['ucastnik1_meno']
        u4_surnames = self.cleaned_data['dataframe']['ucastnik1_priezvisko']
        u4_classes = self.cleaned_data['dataframe']['ucastnik1_rocnik']

        k = len(teams) + 1
        participant_data = [
            [
                u1_names,
                u1_surnames,
                u1_classes
            ],
            [
                u2_names,
                u2_surnames,
                u2_classes
            ],
            [
                u3_names,
                u3_surnames,
                u3_classes
            ],
            [
                u4_names,
                u4_surnames,
                u4_classes
            ]
        ]

        for i in range(1, k):
            team_ = Team.objects.create(
                name=teams[i],
                number=new_number(),
                school=schools[i],
                event=event
            )

            for j in range(int(participants[i])):
                class_ = resolve_class(participant_data[j][2][i])
                comp_ = Compensation.objects.get(
                    event=event,
                    school_class=class_,
                )

                Participant.objects.create(
                    first_name=participant_data[j][0][i],
                    last_name=participant_data[j][1][i],
                    team=team_,
                    compensation=comp_,
                )

