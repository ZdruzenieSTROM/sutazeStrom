from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path

from .views import (CSVResultsView, EventDetailView, EventListView, ExportView,
                    ImportFormView, InitializeView, ResultsView,
                    StatisticsCsvExportView, StatisticsView, SubmitFormView)

app_name = 'competition'

urlpatterns = [
    path('', staff_member_required(EventListView.as_view()), name='index'),
    path('<int:pk>/', staff_member_required(EventDetailView.as_view()), name='event'),
    path('<int:pk>/submit/',
         staff_member_required(SubmitFormView.as_view()), name='submit'),
    path('<int:pk>/results/',
         staff_member_required(ResultsView.as_view()), name='results'),
    path('<int:pk>/csvresults/',
         staff_member_required(CSVResultsView.as_view()), name='csv_results'),
    path('<int:pk>/statistics/',
         staff_member_required(StatisticsView.as_view()), name='statistics'),
    path('<int:pk>/csvstatistics/',
         staff_member_required(StatisticsCsvExportView.as_view()), name='statistics'),
    path('initialize', staff_member_required(
        InitializeView.as_view()), name='initialize'),
    path('import/', staff_member_required(ImportFormView.as_view()), name='import'),
    path('export/', staff_member_required(ExportView.as_view()), name='export'),
]
