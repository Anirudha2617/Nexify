from django.urls import path
from my_forms import views


app_name = 'my_forms'

urlpatterns = [
    #cfreate any form
    # path('edit/', views.form_list, name='form_list'),
    path('create/', views.create_form, name='create_form'),
    path('create/<int:form_id>/extrapage', views.create_extradetails, name='create_extradetails'),

    # #view the form
    path('<int:form_id>/', views.view_form, name='view_form'),
    path('<int:form_id>/fill', views.fill_form, name='fill_form'),
    path('<int:form_id>/<int:response_id>/', views.fill_extradetails, name='fill_extradetails'),
    # path('response/<int:response_id>/', views.view_response, name='view_response'),

    # #Registration details for forms
    path('create/<int:form_id>/registration_details', views.form_registration_details, name='form_registration_details'),
    path('response/<int:form_id>/editregister', views.edit_form_registrationdetails, name='edit_form_register'),

    # #operations on the forms
    path('<int:form_id>/responses/', views.form_responses, name='form_responses'),  # New URL for form submissions
    # path('<int:form_id>/add_questions/', views.add_questions, name='add_questions'),
    # path('<int:form_id>/view_all_questions/', views.view_all_questions, name='view_all_questions'),  # New URL for viewing all questions
    # path('delete_form/<int:form_id>/', views.delete_form, name='delete_form'),



    #     #Notification for both
    path('update_notification/', views.update_notification, name='update_notification'),

    # #register
    # path('response/<int:response_id>/register', views.register, name='register'),


]

