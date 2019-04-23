from django.contrib import messages
from django.core import management
from django.http import FileResponse
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
        saved = form.save()

        messages.success(
            self.request,
            'Údaje boli úspešne importované. Počet tímov: {}, počet účastníkov: {}'.format(
                saved['teams'], saved['participants'])
        )

        return super(ImportFormView, self).form_valid(form)


class ExportView(View):
    def get(self, request):
        filename = 'db.json'
        management.call_command('dumpdata', format='json', output=filename)

        json_file = open(filename, 'rb')

        return FileResponse(json_file, as_attachment=True, filename=filename)
