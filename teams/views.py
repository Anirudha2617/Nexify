from django.shortcuts import render, redirect, get_object_or_404
from club.models import ClubMember, ClubDetails
from teams.models import Team , Notification
from teams.forms import  TeamForm
from django.http import JsonResponse


# Create your views here.
def register(request ,response_id):
    member_in_club = []
    user_in_clubs=ClubMember.objects.filter(user=request.user)
    print(user_in_clubs)
    form = TeamForm(event_id = response_id , leader = request.user)
    return render(request, 'event/registration.html' , {"form": form })


def send_team_notification(request):
    team_id = request.GET.get('team_id', None)
    team = get_object_or_404(Team , pk=team_id)
    notification1 = Notification.create_notification(
        user=request.user,
        title="Approve Request",
        message=f"This is an request to join {team.event.opportunity_title} \n Hosted by {team.event.created_by}",
        notification_type=Notification.INFO,
        sent_from = request.user,
        team = team
    )


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

def delete_team(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    print(request.user.is_superuser)
    # Optional: Restrict deletion to team leader or admin
    if request.user != team.leader and (not request.user.is_superuser): 
        return redirect('event:main_view')
    
    # Delete the team
    event_id = team.event.id
    team.delete()
    return redirect('event:main_view')