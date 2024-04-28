from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('competition.urls')),
]

handler404 = 'competition.views.view_404'
