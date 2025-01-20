from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse , Http404
from .models import Event, Registration_details, Notification
from .forms import EventCreateForm, RegistrationDetailsForm
# from django.forms import modelformset_factory
# from collections import defaultdict
from django.contrib.auth.models import User
from club.models import ClubMember, ClubDetails
from django.http import HttpResponseForbidden , HttpResponseRedirect
# from django.contrib import messages
from django.http import JsonResponse
from my_forms.models import Form
from my_forms.models import Notification as Form_Notifications

from teams.forms import TeamForm
from teams.models import Team
from teams.models import Notification as Team_Notifications


def main_view(request):

    opporttunity_type_data = Event.OPPORTUNITY_TYPES
    opporttunity_type = []
    for i in opporttunity_type_data:
        opporttunity_type.append(i[0])

    created_forms = []
    created_forms = Form.objects.filter(created_by = request.user)
    hosted_events = Event.objects.filter(created_by = request.user)

    # Create an empty queryset for the 'Event' model (or any other model)
    invited_events_responses = request.user.accepted_events.all()
    invited_forms_responses = request.user.accepted_forms.all()
    accepted_teams = request.user.accepted_teams.all() 
    print(accepted_teams)
    created_teams = request.user.created_teams.all()

    #NOTIFICATIONS
    event_notifications = Notification.get_unread_notifications(request.user)
    form_notifications = Form_Notifications.get_unread_notifications(request.user)
    team_notifications = Team_Notifications.get_unread_notifications(request.user)
 
    # Passing the grouped forms to the template
    context = {
        'crated_forms': created_forms,
        'invited_forms_responses': invited_forms_responses,
        'hosted_events': hosted_events,
        'invited_events_responses': invited_events_responses,
        'opportunity_types': opporttunity_type,
        'form_notifications': form_notifications,
        'team_notifications': team_notifications,
        'event_notifications': event_notifications,
        'accepted_teams': accepted_teams,
        'created_teams': created_teams,
        
    }
    return render(request, 'event/main_view.html', context)
    # return HttpResponse("Trying ....")

