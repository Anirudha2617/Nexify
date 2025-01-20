from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse , Http404, HttpResponseForbidden , HttpResponseRedirect
from .forms import FormCreateForm , FormCreateExtraDetails, FormRegistrationDetailsForm
from .models import Form, Question, Answer ,ExtraQuestion, Response, ExtraAnswer, ExtraResponse, ExtraDetails, Registration_details, Notification
# from django.forms import modelformset_factory
# from collections import defaultdict
# from django.contrib.auth.models import User
from club.models import ClubMember, ClubDetails
from django.core.serializers.json import DjangoJSONEncoder
# from django.contrib import messages
from django.http import JsonResponse
import json  # For JSON parsing and validation



def form_registration_details(request ,form_id):

    all_clubs = []

    user_in_clubs=ClubMember.objects.filter(user=request.user)

    for club in user_in_clubs:
        club_detail = ClubDetails.objects.filter(club_pk=club.club.club_pk, branch_pk=club.club.branch_pk).first()
        all_clubs.append(club_detail)

    if request.method == 'POST':
        registration_form = FormRegistrationDetailsForm(request.POST, form_id=form_id, all_clubs = all_clubs)
        if registration_form.is_valid():
            invited_users = registration_form.cleaned_data.get("invited_users",None)
            all_clubs = registration_form.cleaned_data.get('invited_club', None)

            registration_form = registration_form.save(user=request.user , form = get_object_or_404(Form, pk=form_id))

            for club in all_clubs:
                for user in ClubDetails.get_members(club):
                    user = user.user
                    if Notification.get_rejectednotification(request.user, user , registration_form) or ( not Notification.get_notification(request.user, user , registration_form)):
                        notification1 = Notification.create_notification(
                        user=user,
                        title="Approve Request",
                        message=f"This is an request to join {registration_form.form.title} \n Hosted by {registration_form.form.created_by}",                        notification_type=Notification.INFO,
                        sent_from = request.user,
                        event = registration_form
                        )
                        if notification1 :
                            print("notification created for:", user , notification1.id)
                    else:
                        print("notification already exists for:", user)

            print("Registration form created successfully ....................................................................")
            for user in invited_users:
                if Notification.get_rejectednotification(request.user, user , registration_form) or ( not Notification.get_notification(request.user, user , registration_form)):
                    notification1 = Notification.create_notification(
                    user=user,
                    title="Approve Request",
                    message=f"This is an request to join {registration_form.form.title} \n Hosted by {registration_form.form.created_by}",
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
        registration_form = FormRegistrationDetailsForm( form_id = form_id , all_clubs = all_clubs)

    return render(request, 'event/create_registration.html', {'registration_form': registration_form })

def edit_form_registrationdetails(request ,form_id):
    
    print(" yupp..............................................")
    form = get_object_or_404(Form,pk = form_id)
    registration = form.registration_details.all()
    if registration :
        registration = get_object_or_404(Registration_details, pk=registration[0].id)
    else:
        print("Redirectng .......................................................")
        return redirect('my_forms:form_registration_details', form_id = form_id)

    print("Registration Form:",registration)

    if request.user == registration.created_by:
        if request.method == "POST":
            # Bind the form to the POST data
            form = FormRegistrationDetailsForm(request.POST, instance=registration)
            if form.is_valid():
                all_clubs = form.cleaned_data.get('invited_club', None)
                print("All clubs:",all_clubs)
                form = form.save()  # Save changes to the object
                invited_users =form.invited_users.all()
                print("Invited users",invited_users)
                print("Form saved successfully")
                for club in all_clubs:
                    for user in ClubDetails.get_members(club):
                        user = user.user
                        if Notification.get_rejectednotification(request.user, user , registration) or ( not Notification.get_notification(request.user, user , registration)):
                            notification1 = Notification.create_notification(
                            user=user,
                            title="Approve Request",
                            message=f"This is an request to join {form.form.title} \n Hosted by {form.form.created_by}",
                            notification_type=Notification.INFO,
                            sent_from = request.user,
                            event = registration
                            )
                            if notification1 :
                                print("notification created for:", user , notification1.id)
                        else:
                            print("notification already exists for:", user)
                
                for user in invited_users:
                    if (Notification.get_rejectednotification(request.user, user , registration)) or ( not Notification.get_notification(request.user, user , registration)):
                        notification1 = Notification.create_notification(
                        user=user,
                        title="Approve Request",
                        message=f"This is an request to join {form.form.title} \n Hosted by {form.form.created_by}",
                        notification_type=Notification.INFO,
                        sent_from = request.user,
                        event = registration
                        )
                        if notification1 :
                            print("notification created for:", user , notification1.id)
                    else:
                        print("notification already exists for:", user)


            
            return redirect('my_forms:view_form', form_id = registration.form.id)  # Replace with your success page
        else:
            # Prepopulate the form with the object's data
            form = FormRegistrationDetailsForm(instance=registration)
    else:
        print(request.user ,  registration.created_by)
        return HttpResponseForbidden("You are not authorized to edit this .")

    return render(request, 'event/create_registration.html', {'registration_form': form, 'all_clubs_members': None})

# def event_registration_details(request ,response_id):
#     event = get_object_or_404(Response, pk=response_id)
#     if event.form.is_event:
#         pass
#     else:
#         return HttpResponseForbidden
#     all_clubs = []

#     user_in_clubs=ClubMember.objects.filter(user=request.user)

#     for club in user_in_clubs:
#         club_detail = ClubDetails.objects.filter(club_pk=club.club.club_pk, branch_pk=club.club.branch_pk).first()
#         all_clubs.append(club_detail)

#     if request.method == 'POST':
#         registration_form = FormRegistrationDetailsForm(request.POST, form_id=form_id, all_clubs = all_clubs)
#         if registration_form.is_valid():
#             invited_users = registration_form.cleaned_data.get("invited_users",None)
#             all_clubs = registration_form.cleaned_data.get('invited_club', None)

#             registration_form = registration_form.save(user=request.user , form = get_object_or_404(Form, pk=form_id))

#             for club in all_clubs:
#                 for user in ClubDetails.get_members(club):
#                     user = user.user
#                     if Notification.get_rejectednotification(request.user, user , registration_form) or ( not Notification.get_notification(request.user, user , registration_form)):
#                         notification1 = Notification.create_notification(
#                         user=user,
#                         title="Approve Request",
#                         message=f"This is an request to join {registration_form.form.title} \n Hosted by {registration_form.form.created_by}",                        notification_type=Notification.INFO,
#                         sent_from = request.user,
#                         event = registration_form
#                         )
#                         if notification1 :
#                             print("notification created for:", user , notification1.id)
#                     else:
#                         print("notification already exists for:", user)

#             print("Registration form created successfully ....................................................................")
#             for user in invited_users:
#                 if Notification.get_rejectednotification(request.user, user , registration_form) or ( not Notification.get_notification(request.user, user , registration_form)):
#                     notification1 = Notification.create_notification(
#                     user=user,
#                     title="Approve Request",
#                     message=f"This is an request to join {registration_form.form.title} \n Hosted by {registration_form.form.created_by}",
#                     notification_type=Notification.INFO,
#                     sent_from = request.user,
#                     event = registration_form
#                     )
#                     if notification1 :
#                         print("notification created for:", user , notification1.id)
#                 else:
#                     print("notification already exists for:", user)


    

#             return redirect('event:main_view')  # Redirect after saving
#     else:
#         registration_form = FormRegistrationDetailsForm( form_id = form_id , all_clubs = all_clubs)

#     return render(request, 'event/create_registration.html', {'registration_form': registration_form })

# def edit_form_registrationdetails(request ,form_id):
    
#     print(" yupp..............................................")
#     form = get_object_or_404(Form,pk = form_id)
#     registration = form.registration_details.all()
#     if registration :
#         registration = get_object_or_404(Registration_details, pk=registration[0].id)
#     else:
#         print("Redirectng .......................................................")
#         return redirect('my_forms:form_registration_details', form_id = form_id)

#     print("Registration Form:",registration)

#     if request.user == registration.created_by:
#         if request.method == "POST":
#             # Bind the form to the POST data
#             form = FormRegistrationDetailsForm(request.POST, instance=registration)
#             if form.is_valid():
#                 all_clubs = form.cleaned_data.get('invited_club', None)
#                 print("All clubs:",all_clubs)
#                 form = form.save()  # Save changes to the object
#                 invited_users =form.invited_users.all()
#                 print("Invited users",invited_users)
#                 print("Form saved successfully")
#                 for club in all_clubs:
#                     for user in ClubDetails.get_members(club):
#                         user = user.user
#                         if Notification.get_rejectednotification(request.user, user , registration) or ( not Notification.get_notification(request.user, user , registration)):
#                             notification1 = Notification.create_notification(
#                             user=user,
#                             title="Approve Request",
#                             message=f"This is an request to join {form.form.title} \n Hosted by {form.form.created_by}",
#                             notification_type=Notification.INFO,
#                             sent_from = request.user,
#                             event = registration
#                             )
#                             if notification1 :
#                                 print("notification created for:", user , notification1.id)
#                         else:
#                             print("notification already exists for:", user)
                
#                 for user in invited_users:
#                     if (Notification.get_rejectednotification(request.user, user , registration)) or ( not Notification.get_notification(request.user, user , registration)):
#                         notification1 = Notification.create_notification(
#                         user=user,
#                         title="Approve Request",
#                         message=f"This is an request to join {form.form.title} \n Hosted by {form.form.created_by}",
#                         notification_type=Notification.INFO,
#                         sent_from = request.user,
#                         event = registration
#                         )
#                         if notification1 :
#                             print("notification created for:", user , notification1.id)
#                     else:
#                         print("notification already exists for:", user)


            
#             return redirect('my_forms:view_form', form_id = registration.form.id)  # Replace with your success page
#         else:
#             # Prepopulate the form with the object's data
#             form = FormRegistrationDetailsForm(instance=registration)
#     else:
#         print(request.user ,  registration.created_by)
#         return HttpResponseForbidden("You are not authorized to edit this .")

#     return render(request, 'event/create_registration.html', {'registration_form': form, 'all_clubs_members': None})

