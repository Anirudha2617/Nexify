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
    all_titles = []


    #NOTIFICATIONS
    event_notifications = Notification.get_unread_notifications(request.user)
    form_notifications = Form_Notifications.get_unread_notifications(request.user)
 
    # Passing the grouped forms to the template
    context = {
        'crated_forms': created_forms,
        'invited_forms_responses': invited_forms_responses,
        'hosted_events': hosted_events,
        'invited_events_responses': invited_events_responses,
        'all_titles': all_titles,
        'opportunity_types': opporttunity_type,
        'form_notifications': form_notifications,
        'event_notifications': event_notifications,
        
    }
    return render(request, 'event/view_forms.html', context)
    # return HttpResponse("Trying ....")


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


###To be done tomorrow
def register(request ,response_id):
    member_in_club = []
    user_in_clubs=ClubMember.objects.filter(user=request.user)
    print(user_in_clubs)

    return HttpResponse("registration done here")




def update_notification(request):
    notification_id = request.GET.get('notificationId', None)
    action = request.GET.get('action', None)
    
    try:
        notification = get_object_or_404(Notification,id = notification_id)
        if action == "accept":
            notification.perform_action(True)
        elif action == "reject":
            notification.perform_action(False)

        return JsonResponse({'status': 'success', 'message': 'Notification updated successfully'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})




def view_event(request, response_id):
    # Get the Event object using the provided response_id
    response = get_object_or_404(Event, id=response_id)
    
    related_objects = response.event_registration_details.all()
    if related_objects :
        for detail in related_objects:
            registration = detail
            print("Invited Users :", registration.invited_users.all())
    else:
        registration = None
    try:
        is_invited = (request.user in registration.accepted_users.all())
    except:
        is_invited = False

    if (response.created_by == request.user) or (is_invited):  
        
        context = {
            'response': response,
            'response_id': response_id,
            'registration' :registration,
            'user' : request.user,
        }
        return render(request, 'event/response_detail.html', context)
    else:
        return HttpResponseForbidden("You are not authorized to view this event.")

    # Pass the Event object to the template for rendering
    
# from django.shortcuts import render
# from django.core.serializers.json import DjangoJSONEncoder
# import json

def event_registration_details(request ,response_id):
    for user in User.objects.all():
        print(user.id , user.username)
    all_clubs = []

    user_in_clubs=ClubMember.objects.filter(user=request.user)

    for club in user_in_clubs:
        club_detail = ClubDetails.objects.filter(club_pk=club.club.club_pk, branch_pk=club.club.branch_pk).first()
        all_clubs.append(club_detail)

    
    if request.method == 'POST':
        registration_form = RegistrationDetailsForm(request.POST, response_id=response_id, all_clubs = all_clubs)
        if registration_form.is_valid():
            invited_users = registration_form.cleaned_data.get("invited_users",None)
            all_clubs = registration_form.cleaned_data.get('invited_club', None)
            registration_form = registration_form.save()

            for club in all_clubs:
                for user in ClubDetails.get_members(club):
                    user = user.user
                    if Notification.get_rejectednotification(request.user, user , registration_form) or ( not Notification.get_notification(request.user, user , registration_form)):
                        notification1 = Notification.create_notification(
                        user=user,
                        title="Approve Request",
                        message=f"This is an request to join {registration_form.event.opportunity_title} \n Hosted by {registration_form.event.created_by}",
                        notification_type=Notification.INFO,
                        sent_from = request.user,
                        event = registration_form
                        )
                        if notification1 :
                            print("notification created for:", user , notification1.id)
                    else:
                        print("notification already exists for:", user)
                        
            for user in invited_users:
                if Notification.get_rejectednotification(request.user, user , registration_form) or ( not Notification.get_notification(request.user, user , registration_form)):
                    notification1 = Notification.create_notification(
                    user=user,
                    title="Approve Request",
                    message=f"This is an request to join {registration_form.event.opportunity_title} \n Hosted by {registration_form.event.created_by}",
                    notification_type=Notification.INFO,
                    sent_from = request.user,
                    event = registration_form
                    )
                    if notification1 :
                        print("notification created for:", user , notification1.id)
                else:
                    print("notification already exists for:", user)


            return redirect('event:main_view')  # Redirect after saving
    else:
        registration_form = RegistrationDetailsForm( response_id = response_id ,  all_clubs = all_clubs)

    return render(request, 'event/create_registration.html', {'registration_form': registration_form })

def edit_registrationdetails(request ,registration_id):

    print(" yupp..............................................")
    registration = get_object_or_404(Registration_details, pk=registration_id)

    if request.user == registration.event.created_by:
        if request.method == "POST":
            # Bind the form to the POST data
            form = RegistrationDetailsForm(request.POST, instance=registration)
            if form.is_valid():
                all_clubs = form.cleaned_data.get('invited_club', None)

                form = form.save()  # Save changes to the object
                invited_users =form.invited_users.all()
                print("Invited users",invited_users)
                for club in all_clubs:
                    for user in ClubDetails.get_members(club):
                        user = user.user
                        if Notification.get_rejectednotification(request.user, user , registration) or ( not Notification.get_notification(request.user, user , registration)):
                            notification1 = Notification.create_notification(
                            user=user,
                            title="Approve Request",
                            message=f"This is an request to join {form.event.opportunity_title} \n Hosted by {form.event.created_by}",
                            notification_type=Notification.INFO,
                            sent_from = request.user,
                            event = registration
                            )
                            if notification1 :
                                print("notification created for:", user , notification1.id)
                        else:
                            print("notification already exists for:", user)

                for user in invited_users:
                    if Notification.get_rejectednotification(request.user, user , registration) or ( not Notification.get_notification(request.user, user , registration)):
                        notification1 = Notification.create_notification(
                        user=user,
                        title="Approve Request",
                        message=f"This is an request to join {form.event.opportunity_title} \n Hosted by {form.event.created_by}",
                        notification_type=Notification.INFO,
                        sent_from = request.user,
                        event = registration
                        )
                        if notification1 :
                            print("notification created for:", user , notification1.id)
                    else:
                        print("notification already exists for:", user)

                return redirect('event:view_event', response_id = registration.event.id)  # Replace with your success page
        else:
            # Prepopulate the form with the object's data
            form = RegistrationDetailsForm(instance=registration)

        return render(request, 'event/create_registration.html', {'registration_form': form, 'all_clubs_members': None})
    else:
        print(request.user ,  registration.event.created_by)
        return HttpResponseForbidden("You are not authorized to edit this .")
