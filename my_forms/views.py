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
from django.urls import reverse

def trying(request):
    return render(request, 'my_forms/trying.html')

def create_form(request):
    if request.method == 'POST':
        form = FormCreateForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            if form.cleaned_data.get('public'):
                form.instance.is_public = True
            
            # Save the form instance
            new_form = form.save()
        else:
            # Handle form errors
            return render(request, 'my_forms/create_form.html', {'form': form, 'success': False, 'errors': form.errors})

        # Handle dynamic question creation
        num_questions = len([key for key in request.POST if key.startswith("question_text_")])
        
        i=0
        num = 0 
        while (num < num_questions):
        # for i in range(num_questions):
            question_text = request.POST.get(f'question_text_{i}')
            question_type = request.POST.get(f'question_type_{i}')

            if question_text and question_type:
                # Create a question instance
                question = Question.objects.create(
                    form=new_form,
                    text=question_text,
                    question_type=question_type
                )

                # Handle choices for specific question types
                if question_type in ['SC', 'MC', 'DD']:
                    # Retrieve and process choices
                    choices = request.POST.getlist(f'choice_{i}[]')
                    if choices:
                        question.choices = ','.join(choices)
                        question.save()

                elif question_type == 'JSON':
                    # Handle JSON-specific choices
                    json_choices = request.POST.getlist(f'choice_{i}[]')
                    print("Json choices:", json_choices)
                    if json_choices:
                        try:
                            json_choices_str = json.dumps(json_choices)  # Convert list to a JSON string
                            # print("Json choices:", json_choices_str)
                            question.json_choices = json_choices_str    # Validate JSON
                            question.save()
                        except json.JSONDecodeError:
                            # Handle invalid JSON format gracefully
                            print("Saving error...")

                num+=1
                i+=1
            else:
                i+=1
                continue

        # Redirect based on 'extrapage' value
        if request.POST.get('extrapage') == "true":
            return redirect('my_forms:create_extrapage', form_id=new_form.id)
        else:
            return redirect('my_forms:form_registration_details', form_id=new_form.id)

    else:
        form = FormCreateForm(user=request.user)

    context = {
        'form': form,
        'success': True,
    }
    return render(request, 'my_forms/create_form.html', context)

def edit_form(request, form_id):                 ##Condition check done
    form_instance = get_object_or_404(Form, id=form_id, created_by=request.user)
    choice_question_types = ['SC', 'MC', 'DD']  # Question types requiring choices

    questions_queryset = Question.objects.filter(form=form_instance)
    questions = [
        {
            "text": question.text,
            "question_type": question.question_type,
            "choices": question.choices.split(",") if question.choices else (json.loads(question.json_choices) if question.json_choices else []),  # Correctly handle choices
            "id": question.id,
        }
        for question in questions_queryset
    ]
    # print(questions)

    if request.method == 'POST':
        # Initialize the form with POST data
        form = FormCreateForm(request.POST, request.FILES, instance=form_instance, user=request.user)

        if form.is_valid():
            # Handle public status
            if form.cleaned_data.get('public'):
                form.instance.is_public = True

            # Save the form
            updated_form = form.save()

            # Dynamically determine the number of questions
            num_questions = len([key for key in request.POST if key.startswith("question_text_")])
            question_id_list = []
            # Loop through each question in the POST data
            i=0
            num = 0 
            while (num < num_questions):
                print("Entered Question")
            # for i in range(num_questions):
                question_text = request.POST.get(f'question_text_{i}')
                question_type = request.POST.get(f'question_type_{i}')
                question_id = request.POST.get(f'question_id_{i}')  # Check if updating an existing question

                if question_text and question_type:

                    if question_id:
                        # Update existing question
                        question = Question.objects.get(id=question_id, form=form_instance)
                        question.text = question_text
                        question.question_type = question_type
                    else:
                        # Create new question
                        question = Question.objects.create(
                            form=updated_form,
                            text=question_text,
                            question_type=question_type
                        )

                    # Handle choices for specific question types
                    if question_type in choice_question_types:
                        choices = request.POST.getlist(f'choice_{i}[]')  # Get list of choices
                        question.choices = ','.join(choices)  # Store choices as a comma-separated string
                    
                    elif question_type == 'JSON':
                        print("Handling json data....")
                        # Handle JSON-specific choices
                        json_choices = request.POST.getlist(f'choice_{i}[]')
                        print("Json choices:", json_choices)
                        if json_choices:
                            try:
                                json_choices_str = json.dumps(json_choices)  # Convert list to a JSON string
                                print("Json choices:", json_choices_str)
                                question.json_choices = json_choices_str    # Validate JSON
                                question.save()
                            except json.JSONDecodeError:
                                # Handle invalid JSON format gracefully
                                print("Saving error...")
                    else:
                        question.choices = ''  # Clear choices if not applicable
                    question.save()  # Save the question
                    question_id_list.append(question.pk)

                    num+=1
                    i+=1
                else:
                    i+=1
                    continue
                    
            
            #deleting the deleted questions
            all_questions = Question.objects.filter(form=form_instance)
            for question in all_questions:
                if question.id not in question_id_list:
                    question.delete()

            # Redirect based on the 'extrapage' POST data
            return redirect('my_forms:view_form', form_id=updated_form.id)

        # If form is invalid, fall through to rendering with errors
    else:
        # Initialize the form for GET requests
        form = FormCreateForm(instance=form_instance, user=request.user)

    # Context for rendering the template
    context = {
        'form': form,
        'questions': json.dumps(questions, cls=DjangoJSONEncoder),
        'choice_question_types': choice_question_types,
    }

    return render(request, 'my_forms/create_form.html', context)

def fill_form(request, form_id):                  ##Condition check done   for who can fill and how many times
    is_event_personal_details = request.GET.get("is_event_personal_details" , None)
        
    # print("Afdsf",is_event_personal_details)
    form = get_object_or_404(Form, id=form_id)
    is_invited = False
    if form.registration_details.all():
        if request.user in form.registration_details.all()[0].accepted_users.all():
            is_invited = True

    if form.is_public or (form.created_by == request.user) or is_invited :
        if not form.multiple_submissions:
            # print("entered to check if responded")
            responses = Response.objects.filter(form=form, submitted_by = request.user)
            if responses:
                response = responses.first()
                base_url = reverse('my_forms:edit_fill_form', kwargs={'response_id': response.id})
                # Add query parameters for present_page
                if is_event_personal_details:
                    url_with_query = f"{base_url}?is_event_personal_details={is_event_personal_details}"
                return redirect(url_with_query)
                return HttpResponse("You have already submitted this form.")
        # print("Can access to fill form.")
        questions = form.questions.all()
        extradetails = form.extradetails.all()
        total_pages = len(extradetails)
        pages =[]
        for i in extradetails:
            pages.append(i.title)

        if request.method == 'POST':
            # print("submit form")

            response = Response(form=form, submitted_by = request.user)
            # print("Main response saving...")
            response.save()
            # print(response.submitted_by)
            for question in questions:
                update_answers(request, question ,response ,answers  = [] , is_extraanswer = False)

            # print("if extra details present then go to fill extra details with the response id and form id...")
            if total_pages >0:
                return redirect('my_forms:fill_extradetails', form_id=form_id, response_id=response.id)
            else:
                if is_event_personal_details:
                    print("Returning to previous url...")
                    return redirect('event:register' , response_id=is_event_personal_details)
                
                if form.is_event :
                    print("Redirecting to event registration...")
                    return redirect('my_forms:register' , response_id=response.id)
                
                return redirect( 'event:main_view')
                # return HttpResponse(f"Succesfully submitted this response {response.id}")
        else:
            # print("form went to render")
            return render(request, 'my_forms/fill_form.html', {
                'form': form,
                  'questions': questions , 
                  'pages': pages , 
                  'total_pages': len(pages) ,
                  'present_page': -1,
                  'is_event_personal_details': is_event_personal_details,
                  })
    else:
        return HttpResponse("Can't access to fill form.")
        print("Can't access to fill form.")



    pass

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
import json
from .models import Form, Response, Answer

def edit_fill_form(request, response_id):       ##Condition check done fr who can edit            
    # Fetch the response and associated form
    is_event_personal_details = request.GET.get("is_event_personal_details" , None)
    print("Came to edit_fill_form")
    response = get_object_or_404(Response, id=response_id, submitted_by = request.user)
    form = get_object_or_404(Form, id=response.form.id)
    questions = form.questions.all()
    answers = {answer.question.id: answer for answer in response.answers.all()}

    extradetails = form.extradetails.all()
    total_pages = len(extradetails)
    pages = [detail.title for detail in extradetails]

    if request.method == 'POST':
        # print("Processing Edit Form Submission")
        for question in questions:
            update_answers(request, question ,response ,answers , is_extraanswer = False)

        # print("if extra details present then go to fill extra details with the response id and form id...")
        if total_pages >0:
            # print(response.id , form.id)
            # print("Goto to fill extra details")
            responses_all = response.extra_responses.all()
            next_response = None
            for i in responses_all:
                if i.form == extradetails[0]:
                    next_response = i
            if not next_response:
                next_response = response = ExtraResponse.objects.create(form = extradetails[0], response = response)
            # print(responses_all)
            return redirect('my_forms:edit_fill_extradetails', response_id=next_response.id)
        else:
            if is_event_personal_details:
                print("Returning to previous url...")
                return redirect('event:register' , response_id=is_event_personal_details)
            return redirect( 'event:main_view')
            return HttpResponse(f"Succesfully submitted this response {response.id}")

        return redirect('my_forms:view_form', form_id=response.form.id)
    
    print("Returning to")
    return render(request, 'my_forms/fill_form.html', {
        'form': form,
        'questions': questions,
        'pages': pages,
        'total_pages': total_pages,
        'present_page': -1,
        'answers': answers,
    })


def view_form(request, form_id):
    form = get_object_or_404(Form, id=form_id)
    creator = False
    if form.created_by == request.user:
        creator = True

    is_invited = False
    if form.registration_details.all():
        if request.user in form.registration_details.all()[0].accepted_users.all():
            is_invited = True

    registration  = form.registration_details.all()
    if creator:
        submitted_response = Response.objects.filter(form = form)
    else:
        submitted_response = Response.objects.filter(form = form , submitted_by = request.user)
    if registration and creator :
        for detail in registration:
            registration = detail
    else:
        registration = None

    if (creator or is_invited or form.is_public) :   
        print(creator , is_invited , form.is_public)   
        all_extraresponses = form.extradetails.all()
        context = {
            'form': form,
            'all_extraresponses': all_extraresponses,
            'registration' :registration,
            'submitted_response' :submitted_response,
        }
        return render(request ,  'my_forms/view_form.html' , context)
    else:
        return HttpResponseForbidden("You are not authorized to view this Form.")

# def view_response(request, response_id):
#     response = get_object_or_404(Response, id=response_id)
#     related_objects = response.registration_details.all()
#     if related_objects :
#         for detail in related_objects:
#             registration = detail
#     else:
#         registration = None
#     try:
#         is_invited = (request.user in registration.accepted_users.all())
#     except:
#         is_invited = False

#     if (response.submitted_by == request.user) or (is_invited):
#         if (response.submitted_by != request.user) :
#             registration = None
        
        
#         form = get_object_or_404(Form, id=response.form.id)
#         all_extraresponses = response.extra_responses.all()
#         context = {
#             'form': form,
#             'main_response': response,
#             'all_extraresponses': all_extraresponses,
#             'response_id': response_id,
#             'registration' :registration,
#         }
#         return render(request ,  'my_forms/view_response.html' , context)
#     else:
#         return HttpResponseForbidden("You are not authorized to view this response.")

def view_response(request, response_id):
    # Fetch the response and associated form
    is_event_personal_details = request.GET.get("is_event_personal_details" , None)
    print("Came to edit_fill_form")
    response = get_object_or_404(Response, id=response_id, submitted_by = request.user)
    form = get_object_or_404(Form, id=response.form.id)
    questions = form.questions.all()
    answers = {answer.question.id: answer for answer in response.answers.all()}

    extradetails = form.extradetails.all()
    total_pages = len(extradetails)
    pages = [detail.title for detail in extradetails]

    if request.method == 'POST':
        # print("Processing Edit Form Submission")
        for question in questions:
            update_answers(request, question ,response ,answers , is_extraanswer = False)

        # print("if extra details present then go to fill extra details with the response id and form id...")
        if total_pages >0:
            # print(response.id , form.id)
            # print("Goto to fill extra details")
            responses_all = response.extra_responses.all()
            next_response = None
            for i in responses_all:
                if i.form == extradetails[0]:
                    next_response = i
            if not next_response:
                next_response = response = ExtraResponse.objects.create(form = extradetails[0], response = response)
            # print(responses_all)
            return redirect('my_forms:edit_fill_extradetails', response_id=next_response.id)
        else:
            if is_event_personal_details:
                print("Returning to previous url...")
                return redirect('event:register' , response_id=is_event_personal_details)
            return redirect( 'event:main_view')
            return HttpResponse(f"Succesfully submitted this response {response.id}")

        return redirect('my_forms:view_form', form_id=response.form.id)
    
    print("Returning to")
    return render(request, 'my_forms/fill_form.html', {
        'form': form,
        'questions': questions,
        'pages': pages,
        'total_pages': total_pages,
        'present_page': -1,
        'answers': answers,
        'read_only': True
    })

def delete_response(request, response_id):
    try:
        response = Response.objects.get(id=response_id)
        form_id = response.form.id
        response.delete()
        return redirect('my_forms:view_form', form_id = form_id)  # Redirect to the form list after deletion
    except Form.DoesNotExist:
        raise Http404("Form not found")


# Other views...

def form_responses(request, form_id):
    """View to list all submissions of a specific form."""
    form = get_object_or_404(Form, id=form_id)
    responses = form.responses.all()  # Retrieve all responses for this form
    return render(request, 'my_forms/form_responses.html', {'form': form, 'responses': responses})

def delete_form(request, form_id):
    try:
        form = Form.objects.get(id=form_id)
        if request.method == 'POST':
            form.delete()
            return redirect('event:main_view')  # Redirect to the form list after deletion
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


from github_commits.models import Repository
def update_answers(request, question ,response ,answers , is_extraanswer = False):

    # Handle image uploads
    if question.question_type == 'IMG':
        answer_file = request.FILES.get(f'question_{question.id}')
        if answer_file:
            if question.id in answers:
                answer = answers[question.id]
                answer.answer_image = answer_file
                answer.save()
                # print(question , answer)
            else:
                if is_extraanswer:
                    ExtraAnswer.objects.create(response=response, question=question, answer_image=answer_file)
                else:
                    Answer.objects.create(response=response, question=question, answer_image=answer_file)

    # Handle JSON answers (checkboxes)
    elif question.question_type == 'JSON':
        selected_choices = request.POST.getlist(f'question_{question.id}')
        json_choices_str = json.dumps(selected_choices)
        if question.id in answers:
            answer = answers[question.id]
            answer.json_answer = json_choices_str
            answer.save()
            # print(question , answer)
        else:
            if is_extraanswer:
                ExtraAnswer.objects.create(response=response, question=question, json_answer=json_choices_str)
            else:
                Answer.objects.create(response=response, question=question, json_answer=json_choices_str)

    elif question.question_type == 'GITHUB' :
        username = request.POST.get(f'username_{ question.id }')
        repo_id = request.POST.get(f'repo_{ question.id }')
        print("The received repo id in the save form is:",repo_id)
        branch_list = request.POST.get(f'branch_list_{ question.id }').split(',')
        dictionary = {'username': username, 'repo_id': repo_id , 'branch_list': branch_list}
        dictionary = json.dumps(dictionary)
        answer = Answer.objects.create(response=response, question=question, json_answer=dictionary)


    # Handle all other question types (text, textarea, radio, dropdown, datetime)
    else:
        answer_text = request.POST.get(f'question_{question.id}')
        # print(answer_text)
        if question.id in answers:
            answer = answers[question.id]
            answer.answer_text = answer_text
            answer.save()
            # print(question , answer)
        else:
            if is_extraanswer:
                ExtraAnswer.objects.create(response=response, question=question, answer_text=answer_text)
            else:
                Answer.objects.create(response=response, question=question, answer_text=answer_text)


def create_form_events(request):
    event = create_default_form(request.user)
    if not event.responses.filter(submitted_by  = request.user):
        base_url = reverse('my_forms:fill_form', kwargs={'form_id': event.id})
        url_with_query = f"{base_url}"
        return redirect(url_with_query)
    # if request.method == 'POST':
    #     form = FormCreateForm(request.POST, request.FILES, user=request.user)
    #     if form.is_valid():
    #         if form.cleaned_data.get('public'):
    #             form.instance.is_public = True
            
    #         # Save the form instance
    #         new_form = form.save()
    #     else:
    #         # Handle form errors
    #         return render(request, 'my_forms/create_form.html', {'form': form, 'success': False, 'errors': form.errors})

    #     # Handle dynamic question creation
    #     num_questions = len([key for key in request.POST if key.startswith("question_text_")])
        
    #     i=0
    #     num = 0 
    #     while (num < num_questions):
    #     # for i in range(num_questions):
    #         question_text = request.POST.get(f'question_text_{i}')
    #         question_type = request.POST.get(f'question_type_{i}')

    #         if question_text and question_type:
    #             # Create a question instance
    #             question = Question.objects.create(
    #                 form=new_form,
    #                 text=question_text,
    #                 question_type=question_type
    #             )

    #             # Handle choices for specific question types
    #             if question_type in ['SC', 'MC', 'DD']:
    #                 # Retrieve and process choices
    #                 choices = request.POST.getlist(f'choice_{i}[]')
    #                 if choices:
    #                     question.choices = ','.join(choices)
    #                     question.save()

    #             elif question_type == 'JSON':
    #                 # Handle JSON-specific choices
    #                 json_choices = request.POST.getlist(f'choice_{i}[]')
    #                 print("Json choices:", json_choices)
    #                 if json_choices:
    #                     try:
    #                         json_choices_str = json.dumps(json_choices)  # Convert list to a JSON string
    #                         # print("Json choices:", json_choices_str)
    #                         question.json_choices = json_choices_str    # Validate JSON
    #                         question.save()
    #                     except json.JSONDecodeError:
    #                         # Handle invalid JSON format gracefully
    #                         print("Saving error...")

    #             num+=1
    #             i+=1
    #         else:
    #             i+=1
    #             continue

    #     # Redirect based on 'extrapage' value
    #     if request.POST.get('extrapage') == "true":
    #         return redirect('my_forms:create_extrapage', form_id=new_form.id)
    #     else:
    #         return redirect('my_forms:form_registration_details', form_id=new_form.id)

    # else:
    #     form = FormCreateForm(user=request.user)

    # context = {
    #     'form': form,
    #     'success': True,
    # }
    # return render(request, 'my_forms/create_form.html', context)


def create_default_form(user):
    form = Form.objects.create(
        title="Event Form",
        description="Fill your event form",
        form_type="EVENT",
        created_by = user,
        is_event = True,
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