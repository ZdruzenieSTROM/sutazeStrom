from io import StringIO

from django import forms
from django.conf import settings
from pandas import read_csv

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

class ImportForm(forms.Form):
    csv = forms.CharField(widget=forms.Textarea)

    def clean_csv(self):
        csv = self.cleaned_data['csv']

        self.cleaned_data['dataframe'] = read_csv(StringIO(csv), names=CSV_FIELDS, delimiter=settings.CSV_DELIMITER)

        # zavolaj funkciu na kontrolu spravnosti importu

        return csv
