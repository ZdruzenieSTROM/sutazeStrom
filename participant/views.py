import os

from django.conf import settings
from django.contrib import messages
from django.core import management
from django.http import FileResponse, HttpResponse
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
        imported = form.save()

        messages.success(
            self.request,
            'Údaje boli úspešne importované. Počet tímov: {}, počet účastníkov: {}'.format(
                imported['saved_teams'], imported['saved_participants'])
        )

        return super(ImportFormView, self).form_valid(form)


class ExportView(View):
    def get(self, request):
        file_name = 'db' + '.json'
        management.call_command('dumpdata', format='json', output=file_name)
        file_path = os.path.join(settings.BASE_DIR, file_name)

        json_file = open(file_path, 'rb')

        if not os.path.exists(file_path):
            return HttpResponse(status=500)

        return FileResponse(json_file, as_attachment=True, filename=file_name)
