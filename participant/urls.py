from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path

from .views import ExportView, ImportFormView

app_name = 'participant'

urlpatterns = [
    path('import/', staff_member_required(ImportFormView.as_view()), name='import'),
    path('export/', staff_member_required(ExportView.as_view()), name='export'),
]
