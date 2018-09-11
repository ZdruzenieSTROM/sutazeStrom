from django.urls import path

from .views import EventListView, EventDetailView, submit, results

app_name = 'competition'

urlpatterns = [
    path('', EventListView.as_view(), name='index'),
    path('<int:pk>/', EventDetailView.as_view(), name='event'),
    path('<int:pk>/submit', submit, name='submit'),
    path('<int:pk>/results', results, name='results'),
]
