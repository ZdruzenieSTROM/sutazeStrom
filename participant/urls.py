from django.contrib.auth.decorators import login_required
from django.urls import path

from .views import ExportData, ImportData

app_name = 'participant'

urlpatterns = [
    path('import/', login_required(ImportData.as_view()), name='import_data'),
    path('export/', login_required(ExportData.as_view()), name='export_data'),
]
