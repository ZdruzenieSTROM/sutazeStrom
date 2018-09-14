from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path

from .views import EventDetailView, EventListView, ResultsView, SubmitFormView

app_name = 'competition'

urlpatterns = [
    path('', staff_member_required(EventListView.as_view()), name='index'),
    path('<int:pk>/', staff_member_required(EventDetailView.as_view()), name='event'),
    path('<int:pk>/submit', staff_member_required(SubmitFormView.as_view()), name='submit'),
    path('<int:pk>/results', staff_member_required(ResultsView.as_view()), name='results'),
]
