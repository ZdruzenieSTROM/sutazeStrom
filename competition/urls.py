

from django.urls import path

from competition.views import (CertificatesView, CSVResultsView,
                               EventDetailView, EventListView, ExportView,
                               ImportFormView, InitializeView,
                               LatestPublicResultsView, PublicResultsView,
                               ResultsView, StatisticsCsvExportView,
                               StatisticsView, SubmitFormView,
                               nonstaff_redirect_to_public_results)

app_name = 'competition'


urlpatterns = [
    path('', nonstaff_redirect_to_public_results(
        EventListView.as_view()), name='index'),
    path('<int:pk>/', nonstaff_redirect_to_public_results(EventDetailView.as_view()), name='event'),
    path('<int:pk>/submit/',
         nonstaff_redirect_to_public_results(SubmitFormView.as_view()), name='submit'),
    path('<int:pk>/results/',
         nonstaff_redirect_to_public_results(ResultsView.as_view()), name='results'),
    path('priebezne-vysledky',
         nonstaff_redirect_to_public_results(LatestPublicResultsView.as_view()), name='public-results-latest'),
    path('<int:pk>/priebezne-vysledky',
         nonstaff_redirect_to_public_results(PublicResultsView.as_view()), name='public-results'),
    path('<int:pk>/csvresults/',
         nonstaff_redirect_to_public_results(CSVResultsView.as_view()), name='csv_results'),
    path('<int:pk>/statistics/',
         nonstaff_redirect_to_public_results(StatisticsView.as_view()), name='statistics'),
    path('<int:pk>/csvstatistics/',
         nonstaff_redirect_to_public_results(StatisticsCsvExportView.as_view()), name='csv_statistics'),
    path('initialize', nonstaff_redirect_to_public_results(
        InitializeView.as_view()), name='initialize'),
    path('<int:pk>/diplomy',
         nonstaff_redirect_to_public_results(CertificatesView.as_view()), name='certificates'),
    path('import/', nonstaff_redirect_to_public_results(ImportFormView.as_view()), name='import'),
    path('export/', nonstaff_redirect_to_public_results(ExportView.as_view()), name='export'),
]
