from django.urls import path
from event import views
from django.views.generic import TemplateView

app_name = 'event'

urlpatterns = [

    path('', views.main_view, name='main_view'),

    # ##Event creation
    path('event/', views.create_event, name='create_event'),
    # #event function while creation
    path('get-sub-type-choices/', views.get_sub_type_choices, name='get_sub_type_choices'),
    
    # ##event view
    path('event/<int:response_id>/', views.view_event, name='view_event'),


    # #Registration details for events 
    path('create/<int:response_id>/eventregistrationdetails', views.event_registration_details, name='event_registration_details'),
    path('response/<int:registration_id>/editeventregistrationdetail', views.edit_registrationdetails, name='edit_register'),

    # #Notification for both
    path('update_notification/', views.update_notification, name='update_notification'),

    # #register
    path('response/<int:response_id>/register', views.register, name='register'),


]

