from django.urls import path
from my_forms import views
from my_forms import viewsExtradetail
from my_forms import viewsRegistration

app_name = 'my_forms'

urlpatterns = [
    #create any form
    # path('edit/', views.form_list, name='form_list'),
    path('create/', views.create_form, name='create_form'),
    
    path('event/', views.create_form_events, name='create_form_events'),


    path('edit/<int:form_id>', views.edit_form, name='edit_form'),
    path('try/', views.trying, name='try_form'),

    path('create/<int:form_id>/extrapage', viewsExtradetail.create_extrapage, name='create_extrapage'),
    path('edit/<int:form_id>/extrapage', viewsExtradetail.edit_extrapage, name='edit_extrapage'),

    #view the form
    path('<int:form_id>/', views.view_form, name='view_form'),
    path('<int:form_id>/fill', views.fill_form, name='fill_form'),
    path('response/<int:response_id>/edit_fill', views.edit_fill_form, name='edit_fill_form'),
    path('response/<int:response_id>/edit_fill_extradetails', viewsExtradetail.edit_fill_extradetails, name='edit_fill_extradetails'),
    path('response/<int:form_id>/<int:response_id>/', viewsExtradetail.fill_extradetails, name='fill_extradetails'),
    path('response/<int:response_id>/', views.view_response, name='view_response'),
    path('response/<int:response_id>/delete_Response', views.delete_response, name='delete_response'),

    #Registration details for forms
    path('create/<int:form_id>/registration_details', viewsRegistration.form_registration_details, name='form_registration_details'),
    path('response/<int:form_id>/editregister', viewsRegistration.edit_form_registrationdetails, name='edit_form_register'),

    #operations on the forms
    path('<int:form_id>/responses/', views.form_responses, name='form_responses'),  # New URL for form submissions
    path('delete_form/<int:form_id>/', views.delete_form, name='delete_form'),


    #operations on extra responses
    path('delete_extradetails_form/<int:form_id>/', viewsExtradetail.delete_extradetails_form, name='delete_extradetails_form'),


    #Notification for both
    path('update_notification/', views.update_notification, name='update_notification'),

    # #register
    path('response/<int:response_id>/register', views.register, name='register'),


]

