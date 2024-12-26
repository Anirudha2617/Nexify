from django.urls import path
from teams import views

app_name = 'teams'

urlpatterns = [
    path('response/<int:response_id>/register', views.register, name='register'),

    path('send-team-notification', views.send_team_notification, name='send_team_notification'),

    path('update_notification/', views.update_notification, name='update_notification'),
    
    path('<int:team_id>/delete/', views.delete_team, name='delete_team'),

]