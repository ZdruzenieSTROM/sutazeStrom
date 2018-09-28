from django.contrib.auth.decorators import login_required
from django.urls import path

from .views import ExportView, ImportFormView

app_name = 'participant'

urlpatterns = [
    path('import/', login_required(ImportFormView.as_view()), name='import'),
    path('export/', login_required(ExportView.as_view()), name='export'),
]
