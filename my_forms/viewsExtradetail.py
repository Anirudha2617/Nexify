from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse , Http404
from .forms import FormCreateExtraDetails
from .models import Form, ExtraQuestion, Response, ExtraResponse, ExtraDetails
from django.core.serializers.json import DjangoJSONEncoder
import json
from my_forms.views import update_answers
from django.urls import reverse

def create_extrapage(request, form_id):
    #print("Entered my_forms:create_extrapage")
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
        i=0
        num = 0 
        while (num < num_questions):
        # for i in range(num_questions):
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
                
                elif question_type == 'JSON':
                    # Handle JSON-specific choices
                    json_choices = request.POST.getlist(f'choice_{i}[]')
                    # print("Json choices:", json_choices)
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

        #print(request.POST.get('extrapage'))
        # After saving all questions, redirect to the form detail page
        if request.POST.get('extrapage') == "true":
            #print("can proceed with new concepts...")
            form = form.Model
            #print("Form type:",type(form))
            return redirect('my_forms:create_extrapage' ,form_id = form.id)

        if form.Model.registration_details.all():
            return redirect('my_forms:edit_form_register', form_id=form.Model.id)
        else:
            return redirect('my_forms:form_registration_details', form_id=form_id)
    else:
        #print( "creating new forms..." )
        form = FormCreateExtraDetails(mainformid=form_id)
        #print("New form created  ... ")
        
        
    context ={
        'form': form ,
        'success': True,
    }
    return render(request, 'my_forms/create_form.html', context)
    pass



def edit_extrapage(request, form_id):
    # Retrieve the ExtraDetails object and related questions
    form_instance = get_object_or_404(ExtraDetails, id=form_id)
    choice_question_types = ['SC', 'MC', 'DD']  # Question types requiring choices

    questions_queryset = ExtraQuestion.objects.filter(form=form_instance)
    questions = [
        {
            "text": question.text,
            "question_type": question.question_type,
            "choices": question.choices.split(",") if question.choices else (json.loads(question.json_choices) if question.json_choices else []),  # Correctly handle choices
            "id": question.id,
            
        }
        for question in questions_queryset
    ]
    print(questions)

    if request.method == 'POST':
        # Handle form submission for ExtraDetails
        form = FormCreateExtraDetails(request.POST, request.FILES, instance=form_instance, mainformid = form_instance.Model.id)

        if form.is_valid():
            # Save the updated extra details form
            updated_form = form.save()

            # Determine number of questions dynamically
            num_questions = len([key for key in request.POST if key.startswith("question_text_")])
            question_id_list = []

            i=0
            num = 0 
            while (num < num_questions):
                question_text = request.POST.get(f'question_text_{i}')
                question_type = request.POST.get(f'question_type_{i}')
                question_id = request.POST.get(f'question_id_{i}')  # Hidden field to track existing questions

                if question_text and question_type:

                    if question_id:
                        # Update existing question
                        question = ExtraQuestion.objects.get(id=question_id, form=form_instance)
                        question.text = question_text
                        question.question_type = question_type
                    else:
                        # Create new question
                        question = ExtraQuestion.objects.create(
                            form=updated_form,
                            text=question_text,
                            question_type=question_type
                        )

                    # Handle choices for applicable question types
                    if question_type in choice_question_types:
                        choices = request.POST.getlist(f'choice_{i}[]')  # Get list of choices
                        question.choices = ','.join(choices)
                    
                    elif question_type == 'JSON':
                        # Handle JSON-specific choices
                        json_choices = request.POST.getlist(f'choice_{i}[]')
                        # print("Json choices:", json_choices)
                        if json_choices:
                            try:
                                json_choices_str = json.dumps(json_choices)  # Convert list to a JSON string
                                # print("Json choices:", json_choices_str)
                                question.json_choices = json_choices_str    # Validate JSON
                                question.save()
                            except json.JSONDecodeError:
                                # Handle invalid JSON format gracefully
                                print("Saving error...")

                    else:
                        question.choices = ''  # Clear choices for non-choice questions

                    question.save()
                    print(question.pk)
                    question_id_list.append(question.pk)

                    num+=1
                    i+=1
                else:
                    i+=1
                    continue

            # Delete any questions not included in the updated form
            all_questions = ExtraQuestion.objects.filter(form=form_instance)
            for question in all_questions:
                if question.id not in question_id_list:
                    question.delete()

            # Redirect to detail page or reload 
            return redirect('my_forms:view_form', form_id=updated_form.Model.id)
    else:
        # Prepopulate the form for GET requests
        form = FormCreateExtraDetails(instance=form_instance, mainformid = form_instance.Model.id)

    # Render the template
    context = {
        'form': form,
        'questions': json.dumps(questions, cls=DjangoJSONEncoder),
        'choice_question_types': choice_question_types,
    }
    return render(request, 'my_forms/create_form.html', context)


def delete_extradetails_form(request, form_id):
    try:
        form = ExtraDetails.objects.get(id=form_id)
        if form.Model.created_by == request.user or request.user.is_superuser:
            raise Http404("Form not found")

        if request.method == 'POST':
            form.delete()
            previous_url = request.META.get('HTTP_REFERER', '/')
            return redirect(previous_url) # Redirect to the form list after deletion
    except ExtraDetails.DoesNotExist:
        raise Http404("Form not found")


def fill_extradetails(request, form_id, response_id):
    print("Loading filling extra details...")
    present_page = request.POST.get('present_page')
    if present_page is None:
        present_page = 0
    else:
        present_page = int(present_page)

    form = get_object_or_404(Form, id=form_id )
    extradetails = form.extradetails.all()
    extraform = extradetails[present_page]
    extraform = get_object_or_404(ExtraDetails, id=extraform.id)
    total_pages = len(extradetails)
    pages =[]
    for i in extradetails:
        pages.append(i.title)
    questions = extraform.questions.all()

    # print("Extraform_id:" , extraform.id)
    # print("Extradetails length: ",len(extradetails) , present_page)
    # print(questions)

    main_response = get_object_or_404(Response , id = response_id)

    if request.method == 'POST':
        response = ExtraResponse(form = extraform, response = main_response)
        print("Main response saving...")
        response.save()
        print("Response saved............................")
        for question in questions:
            update_answers(request, question ,response ,answers = [] , is_extraanswer = True)

        present_page +=1
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

            return render(request, 'my_forms/fill_form.html', {'form': form, 'questions': questions , 'pages': pages , 'total_pages': len(pages) ,'present_page': present_page})
        else:
            print("goto fill participants details")
            print("Response_id = " , main_response.id)
            return redirect( 'event:main_view')
            return HttpResponse("Succesfully submitted this response")

    else:
        print("form went to render")
        return render(request, 'my_forms/fill_form.html', {'form': form, 'questions': questions , 'pages': pages , 'total_pages': len(pages) ,'present_page': 0})    


def edit_fill_extradetails(request, response_id):
    # Fetch the main response and form
    response = get_object_or_404(ExtraResponse, id=response_id)
    main_response = response.response
    form = get_object_or_404(Form, id=main_response.form.id)


    extradetails = form.extradetails.all()
    total_pages = len(extradetails)
    if response.page_no :
        present_page = response.page_no
    else:
        present_page = int(request.GET.get('present_page', 0))
    # print("This request",  present_page)

    pages = [detail.title for detail in extradetails]
    extraresponse = main_response.extra_responses.all()
    response = extraresponse[present_page]
    extraform = extradetails[present_page]
    questions = extraform.questions.all()
    answers = {answer.question.id: answer for answer in response.answers.all()}
    # print(questions,answers)

    if request.method == 'POST':
        
        for question in questions:
            update_answers(request, question ,response ,answers , is_extraanswer = True )

        # Move to the next page or finalize
        present_page += 1
        if present_page < total_pages:
            extraform = extradetails[present_page]
            next_response = None
            for i in extraresponse:
                if i.form == extraform:
                    next_response = i
            if not next_response:
                next_response = ExtraResponse.objects.create(form = extraform, response = main_response)

            base_url = reverse('my_forms:edit_fill_extradetails', kwargs={'response_id': next_response.id})
            # Add query parameters for present_page
            url_with_query = f"{base_url}?present_page={present_page}"
            return redirect(url_with_query)

        else:
            # Finalize and redirect
            return redirect('my_forms:view_form', form_id=main_response.form.id)

    return render(request, 'my_forms/fill_form.html', {
        'form': form,
        'questions': questions,
        'pages': pages,
        'total_pages': total_pages,
        'present_page': present_page,
        'answers': answers,
    })



# def edit_fill_extradetails(request, response_id):
#     # Fetch the main response and form
#     response = get_object_or_404(ExtraResponse, id=response_id)
#     main_response = response.response
#     form = get_object_or_404(Form, id=main_response.form.id)


#     extradetails = form.extradetails.all()
#     total_pages = len(extradetails)
#     if response.page_no :
#         present_page = response.page_no
#     else:
#         present_page = int(request.GET.get('present_page', 0))
#     print("This request",  present_page)

#     pages = [detail.title for detail in extradetails]
#     extraresponse = main_response.extra_responses.all()
#     response = extraresponse[present_page]
#     extraform = extradetails[present_page]
#     questions = extraform.questions.all()
#     answers = {answer.question.id: answer for answer in response.answers.all()}
#     print(questions,answers)


#     if request.method == 'POST':
#         # Save the current page's answers
#         extra_response = response

#         for question in questions:
#             # Handle image uploads
#             if question.question_type == 'IMG':
#                 answer_file = request.FILES.get(f'question_{question.id}')
#                 if answer_file:
#                     if question.id in answers:
#                         answer = answers[question.id]
#                         answer.answer_image = answer_file
#                         answer.save()
#                         print(question, answer)
#                     else:
#                         ExtraAnswer.objects.create(response=extra_response, question=question, answer_image=answer_file)

#             # Handle JSON answers (checkboxes)
#             elif question.question_type == 'JSON':
#                 selected_choices = request.POST.getlist(f'question_{question.id}')
#                 if selected_choices:
#                     json_choices_str = json.dumps(selected_choices)
#                     if question.id in answers:
#                         answer = answers[question.id]
#                         answer.json_answer = json_choices_str
#                         answer.save()
#                         print(question, answer)
#                     else:
#                         ExtraAnswer.objects.create(response=extra_response, question=question, json_answer=json_choices_str)

#             # Handle all other question types (text, textarea, radio, dropdown, datetime)
#             else:
#                 answer_text = request.POST.get(f'question_{question.id}')
#                 print(answer_text)
#                 if question.id in answers:
#                     answer = answers[question.id]
#                     answer.answer_text = answer_text
#                     answer.save()
#                     print(question, answer_text , answer.answer_text)
#                 else:
#                     ExtraAnswer.objects.create(response=extra_response, question=question, answer_text=answer_text)

#         # Move to the next page or finalize
#         present_page += 1
#         if present_page < total_pages:
#             extraform = extradetails[present_page]
#             base_url = reverse('my_forms:edit_fill_extradetails', kwargs={'response_id': extraresponse[present_page].id})
#             # Add query parameters for present_page
#             url_with_query = f"{base_url}?present_page={present_page}"
#             return redirect(url_with_query)

#         else:
#             # Finalize and redirect
#             return redirect('my_forms:view_form', form_id=main_response.form.id)

#     return render(request, 'my_forms/fill_form.html', {
#         'form': form,
#         'questions': questions,
#         'pages': pages,
#         'total_pages': total_pages,
#         'present_page': present_page,
#         'answers': answers,
#     })

