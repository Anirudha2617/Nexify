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
from my_forms.models import Form , Question
from my_forms.models import Notification as Form_Notifications

from teams.forms import TeamForm
from teams.models import Team
from teams.models import Notification as Team_Notifications
from django.urls import reverse


def create_event(request):   
    event_no = request.GET.get('event_no', None) 
    if not event_no:
        event_no = 1
    if request.method == 'POST':

        print("IN .....................")
        form = EventCreateForm(request.POST, request.FILES )
        if form.is_valid():
            form = form.save(user = request.user)
            print(form.id)
            return redirect( 'event:event_registration_details', response_id=form.id)
            return HttpResponse("Success")  
        else:
            return HttpResponse("Failed")
    else:
        form = EventCreateForm()

    return render(request, 'event/create_event.html', {'form': form ,'event_no': event_no})

from django.shortcuts import get_object_or_404

def edit_event(request, event_id):   
    # Retrieve the event instance to edit
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        # Populate the form with POST data and files
        form = EventCreateForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form = form.save(user=request.user)  # Save the changes
            print(form.id)
            return redirect('event:event_registration_details', response_id=form.id)
        # else:
        #     return HttpResponse("Failed to edit the event" )
    else:
        # Populate the form with the event instance
        form = EventCreateForm(instance=event)

    return render(request, 'event/create_event.html', {'form': form, 'event': event})


def get_sub_type_choices(request):
    opportunity_type = request.GET.get('opportunity_type', None)
    if opportunity_type == "General and case competition":
        choices = Event.GENERAL_SUB_TYPES
    elif opportunity_type == "Scolarships":
        choices = Event.SCHOLARSHIP_SUB_TYPES
    elif opportunity_type == "Hackathon and coding challenge":
        choices = Event.HACKATHON_SUB_TYPES
    else:
        choices = []

    # Convert choices to a JSON-serializable format
    data = [{"value": choice[0], "display": choice[1]} for choice in choices]
    print("Data sent succesfullyyyy")
    return JsonResponse(data, safe=False)

def view_event(request, response_id):             ##Condition checked for users and public
    # Get the Event object using the provided response_id
    event = get_object_or_404(Event, id=response_id)
    
    if event.Registration_detail:
        registration = event.Registration_detail

    else:
        related_objects = event.event_registration_details.all()
        if related_objects :
            registration = related_objects[0]
            event.Registration_detail = registration
            event.save()

        else:
            registration = None
    try:
        is_invited = (request.user in registration.accepted_users.all())
    except:
        is_invited = False

    if (event.created_by == request.user) or (is_invited) or event.is_public() :
        context = {
            'response': event,
            'response_id': response_id,
            'registration' :registration,
            'user' : request.user,
        }

        return render(request, 'event/view_event.html', context)
    else:
        return HttpResponseForbidden("You are not authorized to view this event.")

    # Pass the Event object to the template for rendering

# from django.shortcuts import render
# from django.core.serializers.json import DjangoJSONEncoder
# import json
 
# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Timeline
from .forms import TimelineFormSet


# views.py
from datetime import datetime


###To be done tomorrow
def register(request ,response_id):
    event = get_object_or_404(Event, pk = response_id)
    registration = event.Registration_detail
    from django.utils.timezone import now

    if now() < registration.registration_end or now() > registration.registration_start:
        event.add_members(request.user)
        print(now() < registration.registration_end)
        print(now() > registration.registration_start)
        print(now())
        print(datetime.now())


        
    if request.user in registration.accepted_users.all():
        if not event.user_details_form:
            event.user_details_form = create_default_form(event.created_by)
            event.save()
        if not event.user_details_form.responses.filter(submitted_by  = request.user):
            base_url = reverse('my_forms:fill_form', kwargs={'form_id': event.user_details_form.id})
            # Add query parameters for present_page
            url_with_query = f"{base_url}?is_event_personal_details={response_id}"
            return redirect(url_with_query)
        for team in event.teams.all():
            if request.user in team.accepted_users.all():
                return redirect('event:edit_register' , team_id = team.id)
        else:
            return redirect('event:create_teams' , response_id = response_id)

def create_teams(request , response_id):
    team = None
    event = get_object_or_404(Event , pk=response_id)
    form = get_object_or_404(Form, id=event.user_details_form.id)
    
    if team:
        responses = form.responses.filter(submitted_by__in=team.accepted_users.all())
    else:
        responses = form.responses.filter(submitted_by=request.user)

    if request.method == 'POST':
        team_form = TeamForm(request.POST , event_id = response_id , leader = request.user)
        if team_form.is_valid():
            invited_users = team_form.cleaned_data.get("invited_users",None)
            all_clubs = team_form.cleaned_data.get('invited_club', None)
            team_form = team_form.save()

            for user in invited_users:
                if Team_Notifications.get_rejectednotification(request.user, user , team_form) or ( not Team_Notifications.get_notification(request.user, user , team_form)):
                    notification1 = Team_Notifications.create_notification(
                    user=user,
                    title="Approve Request",
                    message=f"This is an request to join the team {team_form.team_name} \n Hosted by {team_form.leader}",
                    notification_type=Team_Notifications.REQUEST,
                    sent_from = request.user,
                    team = team_form
                    )
                    if notification1 :
                        print("notification created for:", user , notification1.id)
                else:
                    print("notification already exists for:", user)

        return redirect('event:view_event' , response_id = response_id)  # Redirect after saving
    team_form = TeamForm(event_id = response_id , leader = request.user)
    # for response in responses:
    #     if response.submitted_by not in 
    return render(request, 'event/registration.html' , {
        "team_form": team_form , 
        'form': form, 
        'responses': responses,
        'event' : event,
        })


def edit_register(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    event_id = team.event.id
    # Check if the current user is the team leader
    if request.user not in team.accepted_users.all(): 
        return redirect('event:main_view')  # Redirect if unauthorized

    if request.method == 'POST':
        team_form = TeamForm(request.POST, instance=team, event_id=event_id, leader=request.user)
        leave_team = request.POST.get("leave_team", "false") == "true"
        delete_team = request.POST.get("delete_team", "false") == "true"

        if delete_team :
            team.delete()
            return redirect('event:view_event' , response_id = event_id)  # Redirect after deletion

        if not leave_team:
            if (request.POST.get("personal_details", "false") == "true"):
                base_url = reverse('my_forms:fill_form', kwargs={'form_id': team.event.user_details_form.id})
                # Add query parameters for present_page
                url_with_query = f"{base_url}?is_event_personal_details={event_id}"
                return redirect(url_with_query)

            if team_form.is_valid():
                invited_users = team_form.cleaned_data.get("invited_users", None)
                team_form.save()
                
                # Update notifications for invited users
                for user in invited_users:
                    if Team_Notifications.get_rejectednotification(request.user, user, team) or (
                        not Team_Notifications.get_notification(request.user, user, team)):
                        notification = Team_Notifications.create_notification(
                            user=user,
                            title="Approve Request",
                            message=f"This is a request to join the team {team.team_name}\nHosted by {team.leader}",
                            notification_type=Team_Notifications.REQUEST,
                            sent_from=request.user,
                            team=team
                        )
                        if notification:
                            print(Team_Notifications.get_rejectednotification(request.user, user, team) , (not Team_Notifications.get_notification(request.user, user, team)))
                            print("Notification created for:", user, notification.id)
                    else:
                        print("Notification already exists for:", user)
            
        else:
            team.leave_team(request.user)

        return redirect('event:view_event' , response_id = event_id)  # Redirect after saving

    else:
        # Pre-fill the form with the existing team data
        team_form = TeamForm(instance=team, event_id=event_id, leader=request.user)
        event = get_object_or_404(Event , pk=event_id)
        form = get_object_or_404(Form, id=event.user_details_form.id)
        if team:
            responses = form.responses.filter(submitted_by__in=team.accepted_users.all())
        else:
            responses = form.responses.filter(submitted_by=request.user)
    return render(request, 'event/registration.html', {
        'team_form': team_form, 
        'team': team, 
        'edit': True, 
        'form': form, 
        'responses': responses,
        'event': team.event
        })  

def create_default_form(user):
    form = Form.objects.create(
        title="Personal Details",
        description="Fill your personal details",
        form_type="PERSONAL_DETAILS",
        created_by = user,
        multiple_submissions = False
    )
    question_text = ["Name" , "institution" , "Place"]
    for question in question_text:
        Question.objects.create(
            form=form,
            text=question,
            question_type=Question.TEXT,
        )
        
    return form