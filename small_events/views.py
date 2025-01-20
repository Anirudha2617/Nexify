from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def create_event(request ):
        return render(request, 'small_events/create.html', {
        'read_only': True
    })