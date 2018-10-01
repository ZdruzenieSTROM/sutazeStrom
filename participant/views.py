from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import reverse
from django.views import View
from django.views.generic.edit import FormView

from .forms import ImportForm


class ImportFormView(FormView):
    form_class = ImportForm

    template_name = 'participant/import.html'

    def get_success_url(self):
        return reverse('participant:import')

    def form_valid(self, form):
        try:
            form.save()

        except:
            messages.error(
                self.request,
                'Chyba pri ukladaní do databázy!'
            )

        else:
            messages.success(
                self.request,
                'Súbor bol úspešne importovaný'
            )

        return super(ImportFormView, self).form_valid(form)


class ExportView(View):
    def get(self, request):
        return HttpResponse('Tu casom pribudne mozny export dat...')
