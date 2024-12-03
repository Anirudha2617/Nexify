from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse , Http404
from .models import Form, Question, Response, Answer
from .forms import FormCreateForm, FormCreateExtraDetails    #, RegistrationDetailsForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Form, Question, Response, Answer ,ExtraQuestion, ExtraAnswer, ExtraResponse, ExtraDetails
from django.forms import modelformset_factory
from collections import defaultdict
from django.contrib.auth.models import User
from home.models import UserProfile
import json
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
        return redirect('event:form_detail', form_id=form.id)

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
    
    # Passing the grouped forms to the template
    context = {
        'grouped_forms': grouped_forms
    }
    return render(request, 'forms/view_forms.html', context)

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

        return redirect('event:form_detail', form_id=form_id)
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

def form_detail(request, form_id):
    extrapages = False
    present_page = request.POST.get('present_page')
    if present_page is None:
        #print("No response")
        present_page = 0
    else:
        present_page = int(request.POST.get('present_page'))
    #print("Present_page:" , present_page)

    if present_page > 1:
        main_response = request.session.get('main_response')
        print(main_response,"    Main response..................")
        #print("form_id" , form_id)
        extrapages = True
        form = get_object_or_404(Form, id=form_id)
        form = form.extradetails.all()[present_page-1]
        #print("Old Extradetail object created")
        main_form = form.Model
        #print("Got the main form and their lists")
        extradetails = main_form.extradetails.all()
        pages =[]
        for i in extradetails:
            pages.append(i.title)
        #print(type(pages),pages)
        #print(present_page , type(present_page))
        form = extradetails[present_page-1]
        questions = form.questions.all()
            
    else:
        #print("Form object created.")
        form = get_object_or_404(Form, id=form_id)
        questions = form.questions.all()
        extradetails = form.extradetails.all()
        pages =[]
        for i in extradetails:
            pages.append(i.title)
    #preparing the extra details

    # Prepare split choices for multiple choice and dropdown questions
    for question in questions:
        if question.question_type in ['MC', 'DD']:  # MC for multiple choice, DD for dropdown
            question.split_choices = question.choices.split(',') if question.choices else []

    
    if request.method == 'POST':
        if extrapages:
            response = ExtraResponse(form = form , response = main_response)
            print("Added response")
            print("Extra response saving")

        else:
            response = Response(form=form)
            #print("Main response saving...")

        response.save()

        # Process each question's answer
        for question in questions:
  # Handle file upload for images
            if question.question_type == 'IMG':
                answer_file = request.FILES.get(f'question_{question.id}')
                if answer_file:
                    if extrapages:
                        ExtraAnswer.objects.create(response=response, question=question, answer_image=answer_file)
                    else:
                        Answer.objects.create(response=response, question=question, answer_image=answer_file)
            else:
                # Handle text-based answers
                answer_text = request.POST.get(f'question_{question.id}')
                if answer_text:
                    if extrapages:
                        ExtraAnswer.objects.create(response=response, question=question, answer_text=answer_text)
                    else:
                        Answer.objects.create(response=response, question=question, answer_text=answer_text)
        #print("Response submission done...")
        #print("Page length:", len(pages))
        if (present_page < len(pages)):
            

            if present_page == 1 :
                #print("form_id" , form_id)
                form = form.extradetails.all()[present_page-1]
                questions = form.questions.all()
                request.session['main_response'] = response 
                #print(form ,form.id)

                for question in questions:
                    if question.question_type in ['MC', 'DD']:  # MC for multiple choice, DD for dropdown
                        question.split_choices = question.choices.split(',') if question.choices else []

            if present_page > 1 :
                request.session['main_response'] = main_response 
                #print("form_id" , form_id)
                form = main_form.extradetails.all()[present_page-1]
                questions = form.questions.all()
                #print(form ,form.id)

                for question in questions:
                    if question.question_type in ['MC', 'DD']:  # MC for multiple choice, DD for dropdown
                        question.split_choices = question.choices.split(',') if question.choices else []


                
            return render(request, 'forms/form_detail.html', {'form': form, 'questions': questions , 'pages': json.dumps(pages) ,'present_page': present_page})
        else:
            #print("End of pages list")
            return redirect('event:view_forms')
        

        # Redirect to the same form to allow multiple submissions
        # return redirect('form_responses', form_id=form.id)

    return render(request, 'forms/form_detail.html', {'form': form, 'questions': questions , 'pages': json.dumps(pages) ,'present_page': present_page})

def delete_form(request, form_id):
    try:
        form = Form.objects.get(id=form_id)
        if request.method == 'POST':
            form.delete()
            return redirect('event:view_forms')  # Redirect to the form list after deletion
    except Form.DoesNotExist:
        raise Http404("Form not found")


def participants_details(request ,response_id):
    pass

    # if request.method == 'POST':
    #     reg_form = RegistrationDetailsForm(request.POST, user=request.user, form_id=response_id)
    #     if reg_form.is_valid():
    #         print("Registration form created successfully ....................................................................")
    #         reg_form.save()
    #         return redirect('event:view_forms')  # Redirect after saving
    # else:
    #     reg_form = RegistrationDetailsForm(user=request.user, form_id=response_id)

    # return render(request, 'forms/create_registration.html', {'reg_form': reg_form})

def participants_Details(request ,response_id, registration):
    print(registration)