from django.urls import path

from .views import EventDetailView, EventListView, results, submit

app_name = 'competition'

urlpatterns = [
    path('', EventListView.as_view(), name='index'),
    path('<int:pk>/', EventDetailView.as_view(), name='event'),
    path('<int:pk>/submit', submit, name='submit'),
    path('<int:pk>/results', results, name='results'),
]
