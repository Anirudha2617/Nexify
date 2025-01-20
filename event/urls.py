from django.urls import path
from event import views
from event import viewsmain
from event import viewstimeline_notification_registration
from django.views.generic import TemplateView

app_name = 'event'

urlpatterns = [

    path('', viewsmain.main_view, name='main_view'),

    # ##Event creation
    path('event/', views.create_event, name='create_event'),
    path('event/<int:event_id>', views.edit_event, name='edit_event'),
    # #event function while creation
    path('get-sub-type-choices/', views.get_sub_type_choices, name='get_sub_type_choices'),
    
    # ##event view
    path('event/<int:response_id>/', views.view_event, name='view_event'),

    # #Registration details for events 
    path('create/<int:response_id>/eventregistrationdetails', viewstimeline_notification_registration.event_registration_details, name='event_registration_details'),
    path('response/<int:registration_id>/editeventregistrationdetail', viewstimeline_notification_registration.edit_registrationdetails, name='edit_registeration_details'),

    # #Notification for both
    path('update_notification/', viewstimeline_notification_registration.update_notification, name='update_notification'),

    #register
    path('response/<int:response_id>/register', views.register, name='register'),
    path('create_teams/<int:response_id>/register', views.create_teams, name='create_teams'),
    path('edit-team/<int:team_id>/', views.edit_register, name='edit_register'),

    path('timeline/<int:response_id>/', viewstimeline_notification_registration.timeline_create, name='timeline'),
    path('response/timelines/<int:response_id>/', viewstimeline_notification_registration.timeline_list, name='timeline_list'),
    path('timelines/<int:pk>/edit/', viewstimeline_notification_registration.timeline_edit, name='timeline_edit'),
    path('response/timelines/new/<int:response_id>/', viewstimeline_notification_registration.timeline_create, name='timeline_create'),
    path('timelines/<int:pk>/delete/', viewstimeline_notification_registration.timeline_delete, name='timeline_delete'),

]

 