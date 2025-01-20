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


def event_registration_details(request ,response_id):
    all_clubs = []
    event = get_object_or_404(Event, pk = response_id)
    if event.Registration_detail or event.event_registration_details.all() :
        return redirect ("event:edit_registeration_details" , registration_id = event.Registration_detail.id)
        return HttpResponse("Already exists")
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
            registration_form.event.Registration_detail = registration_form

            for club in all_clubs:
                for user in ClubDetails.get_members(club):
                    user = user.user
                    if Notification.get_rejectednotification(request.user, user , registration_form) or ( not Notification.get_notification(request.user, user , registration_form)):
                        notification1 = Notification.create_notification(
                        user=user,
                        title="Approve Request",
                        message=f"This is an request to join {registration_form.event.opportunity_title} \n Hosted by {registration_form.event.created_by}",
                        notification_type=Notification.REQUEST,
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
                    notification_type=Notification.REQUEST,
                    sent_from = request.user,
                    event = registration_form
                    )
                    if notification1 :
                        print("notification created for:", user , notification1.id)
                else:
                    print("notification already exists for:", user)

            # return redirect('event:personal_detail_form' , registration_id = registration_form.id)
            return redirect('event:main_view')  # Redirect after saving
    else:
        registration_form = RegistrationDetailsForm( response_id = response_id ,  all_clubs = all_clubs)

    return render(request, 'event/create_registration.html', {'registration_form': registration_form })

def edit_registrationdetails(request ,registration_id):

    print(" yupp..............................................")
    registration = get_object_or_404(Registration_details, pk=registration_id)
    if registration.event.Registration_detail :
        if registration.event.Registration_detail != registration:
            registration.delete()
    else:
        event = registration.event
        event.Registration_detail = registration
        event.save()


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
                            notification_type=Notification.REQUEST,
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
                        notification_type=Notification.REQUEST,
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

# def personal_detail_form(request , registration_id):


from django.shortcuts import render, redirect, get_object_or_404
from .models import Timeline
from .forms import TimelineForm

def timeline_list(request, response_id):
    timelines = Timeline.objects.filter(response_id=response_id).order_by('date')
    return render(request, 'event/timeline_list.html', {'timelines': timelines})

def timeline_edit(request, pk):
    timeline = get_object_or_404(Timeline, pk=pk)
    if request.method == 'POST':
        form = TimelineForm(request.POST, instance=timeline)
        if form.is_valid():
            form.save()
            return redirect('event:timeline_list', response_id=timeline.response_id)
    else:
        form = TimelineForm(instance=timeline)
    return render(request, 'event/timeline_form.html', {'form': form})

def timeline_create(request, response_id):
    response = get_object_or_404(Event, id=response_id, created_by=request.user)
    timelines = Timeline.timeline( response )
    context = {
        'timelines': timelines,
    }

    if request.method == 'POST':
        num_questions = len([key for key in request.POST if key.startswith("date_")])
        print(num_questions)
        # for i in range(num_questions):
        i=0
        num = 0 
        while (num < num_questions):
            timeline_id = request.POST.get(f'timeline_id{i}')
            timeline_date = request.POST.get(f'date_{i}')
            # timeline_date = localtime(timeline_date)    
            timeline_event = request.POST.get(f'event_{i}')
            if timeline_date:
                num+=1
                i+=1
            else:
                i+=1
                continue


            if timeline_id:
                timeline = Timeline.objects.get(id=timeline_id , response = response)
                timeline.date = timeline_date
                timeline.event = timeline_event
            else:
                timeline = Timeline(date=timeline_date, event=timeline_event, response=response)
            print(timeline_id,timeline_date,timeline_event)
            timeline.save()

            
        return redirect('event:timeline_list', response_id=response_id)


    return render(request, 'event/timelines_create_edit.html', context)

def timeline_delete(request, pk):
    print(f"Deleting timeline with ID: {pk}")
    user_id = request.GET.get('user_id', None)
    timeline = get_object_or_404(Timeline, pk=pk)
    response_id = timeline.response_id
    timeline.delete()
    if user_id:
        return JsonResponse({"message": "Timeline deleted successfully."}, status=200)
        pass
    else:
        return redirect('event:timeline_list', response_id=response_id)

