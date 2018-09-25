from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import ImportData, ExportData

app_name = 'participant'

urlpatterns = [
    path('import/', login_required(ImportData.as_view()), name='import_data'),
    path('export/', login_required(ExportData.as_view()), name='export_data'),
]
