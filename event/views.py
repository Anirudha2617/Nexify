from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse , Http404
from .models import Form, Question, Response, Answer, Registration_details, Notification
from .forms import FormCreateForm, FormCreateExtraDetails , RegistrationDetailsForm, NotificationForm, FormRegistrationDetailsForm, ResponseForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Form, Question, Response, Answer ,ExtraQuestion, ExtraAnswer, ExtraResponse, ExtraDetails
from django.forms import modelformset_factory
from collections import defaultdict
from django.contrib.auth.models import User
from club.models import ClubMember, ClubDetails
from django.http import HttpResponseForbidden , HttpResponseRedirect
from django.contrib import messages
from django.http import JsonResponse


def main_view(request):

    opporttunity_type_data = Response.OPPORTUNITY_TYPES
    opporttunity_type = []
    for i in opporttunity_type_data:
        opporttunity_type.append(i[0])

    crated_forms = Form.objects.filter(created_by = request.user)
    hosted_events = Response.objects.filter(created_by = request.user, form__isnull=True )

    # Create an empty queryset for the 'Event' model (or any other model)
    invited_events = Response.objects.none()
    invited_forms = Response.objects.none()
    
    for i in ((request.user.accepted_events.all())):
        
        
        if i.form:
            accepted_form = Form.objects.filter(id = i.form.id)
            invited_forms = invited_forms | accepted_form
        else:
            accepted_response = Response.objects.filter(id = i.response.id)
            invited_events = invited_events | accepted_response


    all_titles = []
    # for events in all_events:
    #     title = events.form.questions.filter(text = 'Title')
    #     all_titles.append(title)
    

    #NOTIFICATIONS
    all_notifications = Notification.get_unread_notifications(request.user)
 
    # Passing the grouped forms to the template
    context = {
        'crated_forms': crated_forms,
        'invited_forms': invited_forms,
        'hosted_events': hosted_events,
        'invited_events': invited_events,
        'all_titles': all_titles,
        'all_notifications': all_notifications,
        'opportunity_types': opporttunity_type,
        
    }
    return render(request, 'event/view_forms.html', context)
    # return HttpResponse("Trying ....")

def form_list(request):
    """View to list all forms."""
    from django.db.models import Q
    # Assuming `request.user` is the current user
    current_user = request.user
    # Query to get forms created by 'public' or the current user
    forms = Form.objects.all()

    return render(request, 'event/form_list.html', {'forms': forms})

def create_form(request):
    if request.method == 'POST':
        form = FormCreateForm(request.POST, request.FILES, user=request.user)

        if form.is_valid():
            if (form.cleaned_data.get('public') ):
                form.instance.is_public = True
            # Save the form
            new_form = form.save()

            # Redirect to the 'add_questions' view with the newly created form's ID        
        else:
            pass
            #print("some other error")
        form = new_form

        # Determine the number of questions dynamically based on the question_text keys in the POST data
        num_questions = len([key for key in request.POST if key.startswith("question_text_")])
        #print(num_questions )
        # Loop through each question
        for i in range(num_questions):
            question_text = request.POST.get(f'question_text_{i}')
            question_type = request.POST.get(f'question_type_{i}')            
            if question_text and question_type:
                # Create the question instance
                question = Question.objects.create(
                    form=form,
                    text=question_text,
                    question_type=question_type
                )

                # If the question type is Multiple Choice or Dropdown, handle the choices
                if question_type in ['SC','MC', 'DD']:
                    # Retrieve and process choices
                    choices = request.POST.getlist(f'choice_{i}[]')  # Get list of choices
                    question.choices = ','.join(choices)  # Store as a comma-separated string
                    question.save()  # Save the updated question with choices

        #print(request.POST.get('extrapage'))
        # After saving all questions, redirect to the form detail page
        if request.POST.get('extrapage') == "true":
            #print("can proceed with new concepts...")
            return redirect('event:create_extradetails', form_id=form.id)
        else:
            return redirect('event:form_registration_details', form_id=form.id)
    else:
        #print("Hii" , request.user.pk)
        form = FormCreateForm(user=request.user)
        #print("pass")
        
    context ={
        'form': form ,
        'success': True,

    }
    return render(request, 'event/create_form.html', context)

def create_extradetails(request, form_id):
    #print("Entered event:create_extradetails")
    if request.method == 'POST':
        form = FormCreateExtraDetails( request.POST, request.FILES, mainformid = form_id)

        if form.is_valid():
            new_form = form.save()

            # Redirect to the 'add_questions' view with the newly created form's ID        
        else:
            #print("some other error")
            pass
        form = new_form

        # Determine the number of questions dynamically based on the question_text keys in the POST data
        num_questions = len([key for key in request.POST if key.startswith("question_text_")])
        #print(num_questions )
        # Loop through each question
        for i in range(num_questions):
            question_text = request.POST.get(f'question_text_{i}')
            question_type = request.POST.get(f'question_type_{i}')            
            if question_text and question_type:
                # Create the question instance
                question = ExtraQuestion.objects.create(
                    form=form,
                    text=question_text,
                    question_type=question_type
                )

                # If the question type is Multiple Choice or Dropdown, handle the choices
                if question_type in ['SC','MC', 'DD']:
                    # Retrieve and process choices
                    choices = request.POST.getlist(f'choice_{i}[]')  # Get list of choices
                    question.choices = ','.join(choices)  # Store as a comma-separated string
                    question.save()  # Save the updated question with choices

        #print(request.POST.get('extrapage'))
        # After saving all questions, redirect to the form detail page
        if request.POST.get('extrapage') == "true":
            #print("can proceed with new concepts...")
            form = form.Model
            #print("Form type:",type(form))
            return redirect('event:create_extradetails' ,form_id = form.id)


        return redirect('event:form_registration_details', form_id=form_id)
    else:
        #print( "creating new forms..." )
        form = FormCreateExtraDetails(mainformid=form_id)
        #print("New form created  ... ")
        
        
    context ={
        'form': form ,
        'success': True,
    }
    return render(request, 'event/create_extradetails.html', context)
    pass

def fill_form(request, form_id):
        #print("Form object created.")
    form = get_object_or_404(Form, id=form_id)
    questions = form.questions.all()
    extradetails = form.extradetails.all()
    total_pages = len(extradetails)
    pages =[]
    for i in extradetails:
        pages.append(i.title)

    for question in questions:
        if question.question_type in ['MC', 'DD']:  # MC for multiple choice, DD for dropdown
            question.split_choices = question.choices.split(',') if question.choices else []
        
    if request.method == 'POST':
        print(total_pages )
        print("submit form")

        response = Response(form=form, created_by = request.user)
        print("Main response saving...")
        response.save()
        for question in questions:
            if question.question_type == 'IMG':
                answer_file = request.FILES.get(f'question_{question.id}')
                if answer_file:
                    Answer.objects.create(response=response, question=question, answer_image=answer_file)
            else:
                # Handle text-based answers
                answer_text = request.POST.get(f'question_{question.id}')
                if answer_text:
                    Answer.objects.create(response=response, question=question, answer_text=answer_text)

        print("if extra details present then go to fill extra details with the response id and form id...")
        if total_pages >0:
            print(response.id , form.id)
            print("Goto to fill extra details")
            return redirect('event:fill_extradetails', form_id=form_id, response_id=response.id)
        else:
            print("goto fill participants details")
            print("Response_id = " , response.id)
            # return redirect( 'event:registration_details', response_id=response.id)
            return HttpResponse(f"Succesfully submitted this response {response.id}")
    else:
        print("form went to render")
        return render(request, 'event/fill_form.html', {'form': form, 'questions': questions , 'pages': pages , 'total_pages': len(pages) ,'present_page': 0})

    pass

def fill_extradetails(request, form_id, response_id):
    print("Loading filling extra details...")
    present_page = request.POST.get('present_page')
    if present_page is None:
        present_page = 0
    else:
        present_page = int(present_page)
    form = get_object_or_404(Form, id=form_id)
    extradetails = form.extradetails.all()
    print("Extradetails length: ",len(extradetails) , present_page)
    extraform = extradetails[present_page]
    print("Extraform_id:" , extraform.id)
    extraform = get_object_or_404(ExtraDetails, id=extraform.id)
    total_pages = len(extradetails)
    pages =[]
    for i in extradetails:
        pages.append(i.title)
    questions = extraform.questions.all()
    print(questions)
    main_response = get_object_or_404(Response , id = response_id)
    for question in questions:
        if question.question_type in ['MC', 'DD']:  # MC for multiple choice, DD for dropdown
            question.split_choices = question.choices.split(',') if question.choices else []


    if request.method == 'POST':
        response = ExtraResponse(form = extraform, response = main_response)
        print("Main response saving...")
        response.save()
        print("Response saved............................")
        for question in questions:
            if question.question_type == 'IMG':
                answer_file = request.FILES.get(f'question_{question.id}')
                if answer_file:
                    ExtraAnswer.objects.create(response=response, question=question, answer_image=answer_file)
            else:
                # Handle text-based answers
                answer_text = request.POST.get(f'question_{question.id}')
                if answer_text:
                    ExtraAnswer.objects.create(response=response, question=question, answer_text=answer_text)


        present_page +=1
        print(present_page, total_pages)
        if (present_page < total_pages):
            form = form
            extradetails = form.extradetails.all()
            extraform = extradetails[present_page]
            total_pages = len(extradetails)
            pages =[]
            for i in extradetails:
                pages.append(i.title)
            main_response = get_object_or_404(Response, id = response_id)
            questions = extraform.questions.all()
            print(questions)
            for question in questions:
                if question.question_type in ['MC', 'DD']:  # MC for multiple choice, DD for dropdown
                    question.split_choices = question.choices.split(',') if question.choices else []
            print(questions)
            return render(request, 'event/fill_form.html', {'form': form, 'questions': questions , 'pages': pages , 'total_pages': len(pages) ,'present_page': present_page})
        else:
            return HttpResponse("Succesfully submitted this response")


    else:
        print("form went to render")
        return render(request, 'event/fill_form.html', {'form': form, 'questions': questions , 'pages': pages , 'total_pages': len(pages) ,'present_page': 0})    

def view_form(request, form_id):
    form = get_object_or_404(Form, id=form_id)
    registration  = form.registration_details.all()
    if registration :
        for detail in registration:
            registration = detail
    else:
        registration = None

    if (form.created_by == request.user) :      
        all_extraresponses = form.extradetails.all()
        context = {
            'form': form,
            'all_extraresponses': all_extraresponses,
            'registration' :registration,
        }
        return render(request ,  'event/view_form.html' , context)
    else:
        return HttpResponseForbidden("You are not authorized to view this response.")

def view_response(request, response_id):
    response = get_object_or_404(Response, id=response_id)
    related_objects = response.registration_details.all()
    if related_objects :
        for detail in related_objects:
            registration = detail
    else:
        registration = None
    try:
        is_invited = (request.user in registration.accepted_users.all())

    except:
        is_invited = False

    if (response.created_by == request.user) or (is_invited):
        if (response.created_by != request.user) :
            registration = None
        
        
        form = get_object_or_404(Form, id=response.form.id)
        all_extraresponses = response.extra_responses.all()
        context = {
            'form': form,
            'main_response': response,
            'all_extraresponses': all_extraresponses,
            'response_id': response_id,
            'registration' :registration,
        }
        return render(request ,  'event/view_response.html' , context)
    else:
        return HttpResponseForbidden("You are not authorized to view this response.")

def form_registration_details(request ,form_id):

    all_clubs_members = []

    user_in_clubs=ClubMember.objects.filter(user=request.user)

    for club in user_in_clubs:
        club_detail = ClubDetails.objects.filter(club_pk=club.club.club_pk, branch_pk=club.club.branch_pk).first()
        all_members = ClubMember.objects.filter( club = club_detail )
        all_clubs_members.append({
            'club': club_detail,
            'all_members': all_members
        })

    if request.method == 'POST':
        registration_form = FormRegistrationDetailsForm(request.POST, form_id=form_id)
        if registration_form.is_valid():
            invited_users = registration_form.cleaned_data.get("invited_users")

            print("Registration form created successfully ....................................................................")
            registration_form = registration_form.save(user=request.user , form = get_object_or_404(Form, pk=form_id))
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
                if notification1 :
                    print("notification created for:", user , notification1.id)


    

            return redirect('event:view_forms')  # Redirect after saving
    else:
        registration_form = FormRegistrationDetailsForm( form_id = form_id , all_clubs_members = all_clubs_members)

    return render(request, 'event/create_registration.html', {'registration_form': registration_form, 'all_clubs_members': all_clubs_members})

def edit_form_registrationdetails(request ,form_id):
    print(" yupp..............................................")
    form = get_object_or_404(Form,pk = form_id)
    registration = form.registration_details.all()
    if registration :
        registration = get_object_or_404(Registration_details, pk=registration[0].id)
    else:
        print("Redirectng .......................................................")
        return redirect('event:form_registration_details', form_id = form_id)

    print("Registration Form:",registration)


    if request.method == "POST":
        # Bind the form to the POST data
        form = FormRegistrationDetailsForm(request.POST, instance=registration)
        if form.is_valid():
            invited_users = form.cleaned_data.get('invited_users', None)
            form = form.save()  # Save changes to the object
            for user in invited_users:
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


            
            return redirect('event:view_response', response_id = registration.response.id)  # Replace with your success page
    else:
        # Prepopulate the form with the object's data
        form = FormRegistrationDetailsForm(instance=registration)

    return render(request, 'event/create_registration.html', {'registration_form': form, 'all_clubs_members': None})


def add_questions(request, form_id):
    form = get_object_or_404(Form, id=form_id)

    if request.method == 'POST':        
        # Determine the number of questions dynamically based on the question_text keys in the POST data
        num_questions = len([key for key in request.POST if key.startswith("question_text_")])
        
        # Loop through each question
        for i in range(num_questions):
            question_text = request.POST.get(f'question_text_{i}')
            question_type = request.POST.get(f'question_type_{i}')
            
            if question_text and question_type:
                # Create the question instance
                question = Question.objects.create(
                    form=form,
                    text=question_text,
                    question_type=question_type
                )

                # If the question type is Multiple Choice or Dropdown, handle the choices
                if question_type in ['MC', 'DD']:
                    # Retrieve and process choices
                    choices = request.POST.getlist(f'choice_{i}[]')  # Get list of choices
                    question.choices = ','.join(choices)  # Store as a comma-separated string
                    question.save()  # Save the updated question with choices


        # After saving all questions, redirect to the form detail page
        return redirect('event:fill_form', form_id=form.id)

    return render(request, 'apps/event/add_questionss.html', {'form': form})

# Other views...
def view_all_questions(request, form_id):
    form = get_object_or_404(Form, id=form_id)
    questions = form.questions.all()  # Get all the questions related to the form
    return render(request, 'event/view_all_questions.html', {'form': form, 'questions': questions})

def form_responses(request, form_id):
    """View to list all submissions of a specific form."""
    form = get_object_or_404(Form, id=form_id)
    responses = form.responses.all()  # Retrieve all responses for this form
    return render(request, 'event/form_responses.html', {'form': form, 'responses': responses})

def delete_form(request, form_id):
    try:
        form = Form.objects.get(id=form_id)
        if request.method == 'POST':
            form.delete()
            return redirect('event:view_forms')  # Redirect to the form list after deletion
    except Form.DoesNotExist:
        raise Http404("Form not found")

###To be done tomorrow
def register(request ,response_id):
    member_in_club = []
    user_in_clubs=ClubMember.objects.filter(user=request.user)
    print(user_in_clubs)
    for club in user_in_clubs:
        club_detail = ClubDetails.objects.filter(club_pk=club.club.club_pk, branch_pk=club.club.branch_pk).first()
        member_in_club.append({
            'member': club,
            'club_detail': club_detail
            })
    club = member_in_club[0]['club_detail']
    all_members = ClubMember.objects.filter( club = club )

    print(all_members)
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


def get_sub_type_choices(request):
    opportunity_type = request.GET.get('opportunity_type', None)
    if opportunity_type == "General and case competition":
        choices = Response.GENERAL_SUB_TYPES
    elif opportunity_type == "Scolarships":
        choices = Response.SCHOLARSHIP_SUB_TYPES
    elif opportunity_type == "Hackathon and coding challenge":
        choices = Response.HACKATHON_SUB_TYPES
    else:
        choices = []

    # Convert choices to a JSON-serializable format
    data = [{"value": choice[0], "display": choice[1]} for choice in choices]
    print("Data sent succesfullyyyy")
    return JsonResponse(data, safe=False)


def create_event(request):
    event_no = request.GET.get('event_no', None) 
    if not event_no:
        event_no = 1
    if request.method == 'POST':

        print("IN .....................")
        form = ResponseForm(request.POST, request.FILES )
        if form.is_valid():
            form = form.save(user = request.user)
            print(form.id)
            return redirect( 'event:registration_details', response_id=form.id)
            return HttpResponse("Success")
        else:
            return HttpResponse("Failed")
    else:
        form = ResponseForm()

    return render(request, 'event/response_form.html', {'form': form ,'event_no': event_no})

def event_view(request, response_id):
    # Get the Response object using the provided response_id
    response = get_object_or_404(Response, id=response_id)
    related_objects = response.registration_details.all()
    if related_objects :
        for detail in related_objects:
            registration = detail
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
        return HttpResponseForbidden("You are not authorized to view this response.")

    # Pass the Response object to the template for rendering
    
from django.shortcuts import render
from django.core.serializers.json import DjangoJSONEncoder
import json

def registration_details(request ,response_id):
    for user in User.objects.all():
        print(user.id , user.username)
    all_clubs_members = []
    all_clubs = []

    user_in_clubs=ClubMember.objects.filter(user=request.user)

    for club in user_in_clubs:
        club_detail = ClubDetails.objects.filter(club_pk=club.club.club_pk, branch_pk=club.club.branch_pk).first()
        all_clubs.append(club_detail)
        club_detail_dict = {
            'id': club_detail.id,
            'name': club_detail.club_name
        }
        all_members = ClubMember.objects.filter( club = club_detail )
        all_members_list = [
            {'id': member.id, 'name': member.user.username}  # Example fields
            for member in all_members
        ]
        all_clubs_members.append({
            'club': club_detail_dict,
            'all_members': all_members_list
        })
    
    if request.method == 'POST':
        registration_form = RegistrationDetailsForm(request.POST, response_id=response_id, all_clubs = all_clubs)
        if registration_form.is_valid():
            invited_users = registration_form.cleaned_data.get("invited_users")

            print("Registration form created successfully ....................................................................")
            registration_form = registration_form.save()
            for user in invited_users:
                if Notification.get_rejectednotification(request.user, user , registration_form) or ( not Notification.get_notification(request.user, user , registration_form)):
                    notification1 = Notification.create_notification(
                    user=user,
                    title="Approve Request",
                    message=f"This is an request to join {registration_form.response.opportunity_title} \n Hosted by {registration_form.response.created_by}",
                    notification_type=Notification.INFO,
                    sent_from = request.user,
                    event = registration_form
                    )
                    if notification1 :
                        print("notification created for:", user , notification1.id)
                else:
                    print("notification already exists for:", user)


            return redirect('event:view_forms')  # Redirect after saving
    else:
        registration_form = RegistrationDetailsForm( response_id = response_id , all_clubs_members = all_clubs_members,  all_clubs = all_clubs)

    return render(request, 'event/create_registration.html', {'registration_form': registration_form, 'all_clubs_members': json.dumps(all_clubs_members, cls=DjangoJSONEncoder) , 'all_clubs': all_clubs})

def edit_registrationdetails(request ,registration_id):

    print(" yupp..............................................")
    registration = get_object_or_404(Registration_details, pk=registration_id)
    print("Registration Form:",registration)
    if request.user == registration.created_by:
        if request.method == "POST":
            # Bind the form to the POST data
            form = RegistrationDetailsForm(request.POST, instance=registration)
            if form.is_valid():
                invited_users = form.cleaned_data.get('invited_users', None)
                form = form.save()  # Save changes to the object
                for user in invited_users:
                    if Notification.get_rejectednotification(request.user, user , registration) or ( not Notification.get_notification(request.user, user , registration)):
                        notification1 = Notification.create_notification(
                        user=user,
                        title="Approve Request",
                        message=f"This is an request to join {form.response.opportunity_title} \n Hosted by {form.response.created_by}",
                        notification_type=Notification.INFO,
                        sent_from = request.user,
                        event = registration
                        )
                        if notification1 :
                            print("notification created for:", user , notification1.id)
                    else:
                        print("notification already exists for:", user)


                
                return redirect('event:response_detail', response_id = registration.response.id)  # Replace with your success page
        else:
            # Prepopulate the form with the object's data
            form = RegistrationDetailsForm(instance=registration)

        return render(request, 'event/create_registration.html', {'registration_form': form, 'all_clubs_members': None})
    else:
        return HttpResponseForbidden("You are not authorized to edit this .")
