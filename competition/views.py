from django.shortcuts import render

def index(request):
    template = 'competition/index.html'
    return render(request, template, {})
