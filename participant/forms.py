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

def new_number():
    pass

class ImportForm(forms.Form):
    csv_text = forms.CharField(widget=forms.Textarea, required=False, label='')
    csv_file = forms.FileField(required=False, label='')
    event = forms.ModelChoiceField(queryset=Event.objects.all())

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

    def save(self):
        event = self.cleaned_data['event']
        teams = self.cleaned_data['dataframe']['tim']
        schools = self.cleaned_data['dataframe']['skola']
        participants = self.cleaned_data['dataframe']['pocet_clenov']

        k = len(teams)
        for i in range(k):
            team_ = Team.objects.create(
                name=teams[i],
                number=new_number(),
                school=schools[i],
                event=event
            )

        # daco dalsie
