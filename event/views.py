from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse , Http404
from .models import Form, Question, Response, Answer, Registration_details, Notification
from .forms import FormCreateForm, FormCreateExtraDetails , RegistrationDetailsForm, NotificationForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Form, Question, Response, Answer ,ExtraQuestion, ExtraAnswer, ExtraResponse, ExtraDetails
from django.forms import modelformset_factory
from collections import defaultdict
from django.contrib.auth.models import User
from club.models import ClubMember, ClubDetails
from django.http import HttpResponseForbidden , HttpResponseRedirect
from django.contrib import messages

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
    return render(request, 'forms/view_all_questions.html', {'form': form, 'questions': questions})

def form_responses(request, form_id):
    """View to list all submissions of a specific form."""
    form = get_object_or_404(Form, id=form_id)
    responses = form.responses.all()  # Retrieve all responses for this form
    return render(request, 'forms/form_responses.html', {'form': form, 'responses': responses})

def view_forms(request):

    # Assuming the Form model has a 'form_type' attribute
    # Group forms by their 'form_type' attribute
    form_types = Form.objects.values('form_type').distinct()  # Get distinct form types
    
    grouped_forms = {}  # Dictionary to hold grouped forms
    
    for form_type in form_types:
        forms = Form.objects.filter(form_type=form_type['form_type'])
        grouped_forms[form_type['form_type']] = forms  # Group forms by type
    
    print("Events" , Response.get_forms(request.user))

    all_events = Response.objects.filter(created_by = request.user, form__isnull=True )
    all_titles = []
    # for events in all_events:
    #     title = events.form.questions.filter(text = 'Title')
    #     all_titles.append(title)
    

    #NOTIFICATIONS
    all_notifications = Notification.get_unread_notifications(request.user)
 
    # Passing the grouped forms to the template
    context = {
        'grouped_forms': grouped_forms,
        'all_events': all_events,
        'all_titles': all_titles,
        'all_notifications': all_notifications,
        
    }
    return render(request, 'forms/view_forms.html', context)
    # return HttpResponse("Trying ....")

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
        return render(request ,  'forms/view_response.html' , context)
    else:
        return HttpResponseForbidden("You are not authorized to view this response.")

def form_list(request):
    """View to list all forms."""
    from django.db.models import Q

    # Assuming `request.user` is the current user
    current_user = request.user

    # Query to get forms created by 'public' or the current user
    forms = Form.objects.all()

    return render(request, 'forms/form_list.html', {'forms': forms})

def create_form(request):
    if request.method == 'POST':
        form = FormCreateForm(request.POST, request.FILES, user=request.user)

        if form.is_valid():
            if (form.cleaned_data.get('public') ):
                form.instance.created_by = None
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
            return redirect('event:participants_details', form_id=form.id)
    else:
        #print("Hii" , request.user.pk)
        form = FormCreateForm(user=request.user)
        #print("pass")
        
    context ={
        'form': form ,
        'success': True,
    }
    return render(request, 'forms/create_form.html', context)

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

        return redirect('event:fill_form', form_id=form_id)
    else:
        #print( "creating new forms..." )
        form = FormCreateExtraDetails(mainformid=form_id)
        #print("New form created  ... ")
        
        
    context ={
        'form': form ,
        'success': True,
    }
    return render(request, 'forms/create_extradetails.html', context)
    pass

# def form_detail(request, form_id):
#     extrapages = False
#     present_page = request.POST.get('present_page')
#     if present_page is None:
#         #print("No response")
#         present_page = 0
#     else:
#         present_page = int(request.POST.get('present_page'))
#     #print("Present_page:" , present_page)

#     if present_page > 1:
#         main_response = request.session.get('main_response')
#         print(main_response,"    Main response..................")
#         #print("form_id" , form_id)
#         extrapages = True
#         form = get_object_or_404(Form, id=form_id)
#         form = form.extradetails.all()[present_page-1]
#         #print("Old Extradetail object created")
#         main_form = form.Model
#         #print("Got the main form and their lists")
#         extradetails = main_form.extradetails.all()
#         pages =[]
#         for i in extradetails:
#             pages.append(i.title)
#         #print(type(pages),pages)
#         #print(present_page , type(present_page))
#         form = extradetails[present_page-1]
#         questions = form.questions.all()
            
#     else:
#         #print("Form object created.")
#         form = get_object_or_404(Form, id=form_id)
#         questions = form.questions.all()
#         extradetails = form.extradetails.all()
#         pages =[]
#         for i in extradetails:
#             pages.append(i.title)
#     #preparing the extra details

#     # Prepare split choices for multiple choice and dropdown questions
#     for question in questions:
#         if question.question_type in ['MC', 'DD']:  # MC for multiple choice, DD for dropdown
#             question.split_choices = question.choices.split(',') if question.choices else []

    
#     if request.method == 'POST':
#         if extrapages:
#             response = ExtraResponse(form = form , response = main_response)
#             print("Added response")
#             print("Extra response saving")

#         else:
#             response = Response(form=form)
#             #print("Main response saving...")

#         response.save()

#         # Process each question's answer
#         for question in questions:
#   # Handle file upload for images
#             if question.question_type == 'IMG':
#                 answer_file = request.FILES.get(f'question_{question.id}')
#                 if answer_file:
#                     if extrapages:
#                         ExtraAnswer.objects.create(response=response, question=question, answer_image=answer_file)
#                     else:
#                         Answer.objects.create(response=response, question=question, answer_image=answer_file)
#             else:
#                 # Handle text-based answers
#                 answer_text = request.POST.get(f'question_{question.id}')
#                 if answer_text:
#                     if extrapages:
#                         ExtraAnswer.objects.create(response=response, question=question, answer_text=answer_text)
#                     else:
#                         Answer.objects.create(response=response, question=question, answer_text=answer_text)
#         #print("Response submission done...")
#         #print("Page length:", len(pages))
#         if (present_page < len(pages)):
            

#             if present_page == 1 :
#                 #print("form_id" , form_id)
#                 form = form.extradetails.all()[present_page-1]
#                 questions = form.questions.all()
#                 request.session['main_response'] = response 
#                 #print(form ,form.id)

#                 for question in questions:
#                     if question.question_type in ['MC', 'DD']:  # MC for multiple choice, DD for dropdown
#                         question.split_choices = question.choices.split(',') if question.choices else []

#             if present_page > 1 :
#                 request.session['main_response'] = main_response 
#                 #print("form_id" , form_id)
#                 form = main_form.extradetails.all()[present_page-1]
#                 questions = form.questions.all()
#                 #print(form ,form.id)

#                 for question in questions:
#                     if question.question_type in ['MC', 'DD']:  # MC for multiple choice, DD for dropdown
#                         question.split_choices = question.choices.split(',') if question.choices else []


                
#             return render(request, 'forms/form_detail.html', {'form': form, 'questions': questions , 'pages': json.dumps(pages) ,'present_page': present_page})
#         else:
#             #print("End of pages list")
#             return redirect('event:view_forms')
        

#         # Redirect to the same form to allow multiple submissions
#         # return redirect('form_responses', form_id=form.id)

#     return render(request, 'forms/form_detail.html', {'form': form, 'questions': questions , 'pages': json.dumps(pages) ,'present_page': present_page})

def delete_form(request, form_id):
    try:
        form = Form.objects.get(id=form_id)
        if request.method == 'POST':
            form.delete()
            return redirect('event:view_forms')  # Redirect to the form list after deletion
    except Form.DoesNotExist:
        raise Http404("Form not found")

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
            return HttpResponse("Succesfully submitted this response")
    else:
        print("form went to render")
        return render(request, 'forms/fill_form.html', {'form': form, 'questions': questions , 'pages': pages , 'total_pages': len(pages) ,'present_page': 0})

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
            return render(request, 'forms/fill_form.html', {'form': form, 'questions': questions , 'pages': pages , 'total_pages': len(pages) ,'present_page': present_page})
        else:
            return HttpResponse("Succesfully submitted this response")


    else:
        print("form went to render")
        return render(request, 'forms/fill_form.html', {'form': form, 'questions': questions , 'pages': pages , 'total_pages': len(pages) ,'present_page': 0})    

def registration_details(request ,response_id):

    all_clubs_members = []

    user_in_clubs=ClubMember.objects.filter(user=request.user)

    for club in user_in_clubs:
        club_detail = ClubDetails.objects.filter(club_pk=club.club.club_pk, branch_pk=club.club.branch_pk).first()
        all_members = ClubMember.objects.filter( club = club_detail )
        all_clubs_members.append({
            'club': club_detail,
            'all_members': all_members
        })
    # for i in all_clubs_members:
    #     print(i)

    
    if request.method == 'POST':
        registration_form = RegistrationDetailsForm(request.POST, response_id=response_id)
        if registration_form.is_valid():
            invited_users = registration_form.cleaned_data.get("invited_users")

            print("Registration form created successfully ....................................................................")
            registration_form = registration_form.save()
            for user in invited_users:
                if Notification.get_notification(request.user, user , registration_form):
                    pass
                notification1 = Notification.create_notification(
                user=user,
                title="Approve Request",
                message=f"This is an request to join {registration_form.response.form.title} \n Hosted by {registration_form.response.created_by}",
                notification_type=Notification.INFO,
                sent_from = request.user,
                event = registration_form
                )
                if notification1 :
                    print("notification created for:", user , notification1.id)


    

            return redirect('event:view_forms')  # Redirect after saving
    else:
        registration_form = RegistrationDetailsForm( response_id = response_id , all_clubs_members = all_clubs_members)

    return render(request, 'forms/create_registration.html', {'registration_form': registration_form, 'all_clubs_members': all_clubs_members})

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


def edit_registrationdetails(request ,registration_id):

    print(" yupp..............................................")
    registration = get_object_or_404(Registration_details, pk=registration_id)
    print("Registration Form:",registration)

    if request.method == "POST":
        # Bind the form to the POST data
        form = RegistrationDetailsForm(request.POST, instance=registration)
        if form.is_valid():

            invited_users = form.cleaned_data.get('invited_users', None)
            form = form.save()  # Save changes to the object
            for user in invited_users:
                if Notification.get_notification(request.user, user , registration):
                    pass
                else:
                    notification1 = Notification.create_notification(
                    user=user,
                    title="Approve Request",
                    message=f"This is an request to join {form.response.form.title} \n Hosted by {form.response.created_by}",
                    notification_type=Notification.INFO,
                    sent_from = request.user,
                    event = registration
                    )
                    if notification1 :
                        print("notification created for:", user , notification1.id)


            
            return redirect('event:view_response', response_id = registration.response.id)  # Replace with your success page
    else:
        # Prepopulate the form with the object's data
        form = RegistrationDetailsForm(instance=registration)

    return render(request, 'forms/create_registration.html', {'registration_form': form, 'all_clubs_members': None})



from django.http import JsonResponse
from django.shortcuts import render

def handle_notification(request):
    if request.method == "POST":
        # Filter out all keys that start with "card-"
        card_states = {key: value for key, value in request.POST.items() if key.startswith('card-')}

        # Process each notification state
        for card_id, action in card_states.items():
            notification_id = card_id.replace('card-', '')  # Extract the ID
            notification = get_object_or_404(Notification,id = notification_id)
            if action == "accept":
                notification.status = True
                notification.mark_as_read()
                notification.perform_action()
            elif action == "reject":
                notification.status = False
                notification.mark_as_read()
                notification.perform_action()
            print(f"Notification ID: {notification_id}, Action: {action}")
            # Add your logic here to mark as accepted/rejected, etc.
            
        previous_url = request.META.get('HTTP_REFERER', '/default-url/')  # Fallback URL in case the referer is not available
        return HttpResponseRedirect(previous_url)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)



from django.http import JsonResponse
from .models import Response

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


from .forms import ResponseForm

def response_form_view(request):
    if request.method == 'POST':

        print("IN .....................")
        form = ResponseForm(request.POST, request.FILES )
        if form.is_valid():
            form = form.save(user  =  request.user)
            print(form.id)
            return HttpResponse("Success")
        else:
            return HttpResponse("Failed")
    else:
        form = ResponseForm()

    return render(request, 'forms/response_form.html', {'form': form})

def response_detail_view(request, response_id):
    # Get the Response object using the provided response_id
    response = get_object_or_404(Response, pk=response_id)

    # Pass the Response object to the template for rendering
    return render(request, 'forms/response_detail.html', {'response': response})


