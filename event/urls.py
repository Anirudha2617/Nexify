from django.urls import path
from event import views
from django.views.generic import TemplateView

app_name = 'event'

urlpatterns = [
    #cfreate any form
    path('', views.main_view, name='view_forms'),
    path('edit/', views.form_list, name='form_list'),
    path('create/', views.create_form, name='create_form'),
    path('create/<int:form_id>/extrapage', views.create_extradetails, name='create_extradetails'),

    #view the form
    path('form/<int:form_id>/', views.view_form, name='view_form'),
    path('<int:form_id>/', views.fill_form, name='fill_form'),
    path('<int:form_id>/<int:response_id>/', views.fill_extradetails, name='fill_extradetails'),
    path('response/<int:response_id>/', views.view_response, name='view_response'),

    #Registration details for forms
    path('create/<int:form_id>/registration_details', views.form_registration_details, name='form_registration_details'),
    path('response/<int:form_id>/editregister', views.edit_form_registrationdetails, name='edit_form_register'),

    #operations on the forms
    path('<int:form_id>/responses/', views.form_responses, name='form_responses'),  # New URL for form submissions
    path('<int:form_id>/add_questions/', views.add_questions, name='add_questions'),
    path('<int:form_id>/view_all_questions/', views.view_all_questions, name='view_all_questions'),  # New URL for viewing all questions
    path('delete_form/<int:form_id>/', views.delete_form, name='delete_form'),





    ##Event creation
    path('event/', views.create_event, name='response_form'),
    #event function while creation
    path('get-sub-type-choices/', views.get_sub_type_choices, name='get_sub_type_choices'),
    
    ##event view
    path('event/<int:response_id>/', views.event_view, name='response_detail'),


    #Registration details for events 
    path('create/<int:response_id>/eventregistrationdetails', views.registration_details, name='registration_details'),
    path('response/<int:registration_id>/editeventregistrationdetail', views.edit_registrationdetails, name='edit_register'),

    #Notification for both
    path('update_notification/', views.update_notification, name='update_notification'),

    #register
    path('response/<int:response_id>/register', views.register, name='register'),


]

