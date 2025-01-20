from django.db import models
from django.contrib.auth.models import User
from event.models import Event
from django.http import HttpResponse

# Create your models here.

class Team(models.Model):
    event = models.ForeignKey(Event, related_name = 'teams', on_delete = models.CASCADE)
    team_name = models.CharField(max_length=20 , null= False, blank=False)
    description = models.TextField(max_length=200, null=True, blank=True)
    leader = models.ForeignKey(User , related_name = "leading_team" , on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, related_name='created_teams', on_delete=models.CASCADE ,blank=True , null=True)
    invited_users = models.ManyToManyField(User, related_name='invited_teams', blank=True)
    accepted_users = models.ManyToManyField(User, related_name='accepted_teams', blank=True)
    rejected_users = models.ManyToManyField(User, related_name='rejected_teams', blank=True)
    open = models.BooleanField(default=0)

    def __str__(self):
        return self.team_name

    def list_members(self):
        all_members = self.event.event_registration_details.all()[0].accepted_users.all()
        list = []
        for member in all_members:
            list.append(member)
        return list 
    
    def leave_team(self, user):
        if user!=self.leader :
            self.accepted_users.remove(user)
            self.save()
        else:
            return HttpResponse("You are the leader, you can't leave!")

    @classmethod
    def not_in_any_team(cls, event):
        # Get all accepted users for the event
        all_users = event.event_registration_details.first().accepted_users.all()

        # Get all users who are already in a team
        
        users_in_teams = User.objects.filter(
            id__in=Team.objects.filter(event=event)
            .values_list("accepted_users__id", flat=True))

        # Exclude users who are already in a team
        users_not_in_any_team = all_users.exclude(id__in=users_in_teams)

        return users_not_in_any_team
    def save(self, *args, **kwargs):
        # Save the object first to ensure it has a primary key
        if not self.pk:
            super().save(*args, **kwargs)

        # Add the leader to the accepted_users if not already present
        if self.leader not in self.accepted_users.all():
            self.accepted_users.add(self.leader)

        # Save again after updating many-to-many relationships
        return super().save(*args, **kwargs)


class Notification(models.Model):
    # Notification types
    INFO = 'info'
    REQUEST = 'request'
    WARNING = 'warning'
    ERROR = 'error' 
    SUCCESS = 'success'

    NOTIFICATION_TYPES = [
        (INFO, 'Info'),
        (WARNING, 'Warning'),
        (ERROR, 'Error'),
        (SUCCESS, 'Success'),
        (REQUEST , 'request'),
    ]

    # Fields
    sent_from = models.ForeignKey(User, related_name = 'team_notification', on_delete=models.CASCADE )
    team = models.ForeignKey(Team, related_name = 'team_notifications', on_delete=models.CASCADE , null =True , blank = True)
    user = models.ForeignKey(User, related_name = 'team_notifications', on_delete=models.CASCADE )
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default=INFO)
    is_read = models.BooleanField(default=False)
    status = models.BooleanField(null= True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}: {self.status}"

    # Methods
    def mark_as_read(self):
        self.is_read = True
        self.save()

    def mark_as_unread(self):
        self.is_read = False
        self.save()

    @classmethod
    def create_notification(cls, user, title, message, sent_from, team, notification_type=INFO ):
        return cls.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            sent_from=sent_from,
            team = team,
        )

    @classmethod
    def get_unread_notifications(cls, user):
         return cls.objects.filter(user=user , is_read = False)


    @classmethod
    def get_all_notifications(cls, user):
         return cls.objects.filter(user=user)

    @classmethod
    def mark_all_as_read(cls, user):
        cls.objects.filter(user=user, is_read=False).update(is_read=True)

    @classmethod
    def get_rejectednotification(cls, sent_by,sent_to, team ):
        try:
            a = cls.objects.filter(sent_from=sent_by, team=team , user = sent_to , status = False)
            from django.db.models import Q
            a = a.filter(Q(status=False) | Q(status__isnull=True))
        except:
            a= None
        return a
    
    @classmethod
    def get_notification(cls, sent_by,sent_to,team ):
        try:
            a = cls.objects.filter(sent_from=sent_by, team=team, user = sent_to )
        except:
            a = None
        return a

    def perform_action(self , status):
        """
        Perform action based on the `action_button` value.
        """
        print("Performing actions...")
        self.status = status
        self.mark_as_read()
        if self.status:
            print("accepted")
            return self.action_true()
            
        else:
            print("rejected")
            return self.action_false()

    def action_true(self):
        self.mark_as_read()
        self.team.invited_users.remove(self.user)
        # print("Removed user from invited_users list")
        if not self.team.accepted_users.filter(id=self.user.id).exists():
            self.team.accepted_users.add(self.user)
        print("accepted")
        
        self.save()
        # print("Action accepted!")


    def action_false(self):
        self.mark_as_read()
        print("rejected")
        # Action when `action_button` is False
        self.team.invited_users.remove(self.user)
        if self.user not in self.team.rejected_users:
            self.team.rejected_users.add(self.user)
        print("Action rejected!")

