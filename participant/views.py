from functools import reduce
import pandas

from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import HttpResponse

from django.views import View
from .models import Team
from competition.models import Event, Problem


class ImportData(View):
    template = 'participant/import.html'

    def post(self, request):
        csv_file = request.FILES["csv_file"]
        if not csv_file.name.endswith('.csv'):
            messages.add_message(request, messages.ERROR, 'Súbor musí byť typu CSV!')
            return render(request, self.template)

        try:
            self.handle_csv(csv_file)
        except:
            messages.add_message(request, messages.ERROR, 'Vyskytla sa neočakávaná chyba, skús to znova.')
        else:
            messages.add_message(request, messages.SUCCESS, 'Databáza bola úspešne importovaná.')

        return redirect('participant:import_data')

    def get(self, request):
        return render(request, self.template)

    def handle_csv(self, csv_file):
        colnames = [
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
        # tim, skola, pocet_clenov, ucastnik_meno, ucastnik_priezvisko, ucastnik_rocnik
        data = pandas.read_csv(csv_file, sep=';', encoding='iso8859_2', names=colnames)

        # some action...


class ExportData(View):
    def get(self, request):
        return HttpResponse('Tu casom pribudne mozny export dat...')
