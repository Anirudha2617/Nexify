from django.db import models
from django.contrib.auth.models import User

class ClubData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='club_data_by_user')
    fixed_json_metadata=models.TextField(default='"class": "go.TreeModel","nodeDataArray":',blank=True,null=True)
    json_data = models.TextField(default='{"class": "go.TreeModel", "nodeDataArray": []}',)

    def __str__(self):
        return str(self.json_data)


from django.db import models
from django.contrib.auth.models import User
import uuid

class ClubDetails(models.Model):
    club_pk = models.IntegerField()
    branch_pk = models.IntegerField()

    background_image = models.ImageField(
        upload_to='clubs_background/', blank=True, null=True,
        default='../static/assets/img/club_default/background.jpeg'
    )
    logo_image = models.ImageField(
        upload_to='clubs_logo/', blank=True, null=True,
        default='../static/assets/img/club_default/logo.jpeg'
    )

    club_name = models.CharField(max_length=100, unique=True)
    club_subtext = models.CharField(max_length=100, blank=True)
    club_description = models.TextField(max_length=500, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Club Detail"
        verbose_name_plural = "Club Details"
        ordering = ['club_name']
        indexes = [
            models.Index(fields=['club_name']),
            models.Index(fields=['club_pk', 'branch_pk'])
        ]

    def __str__(self):
        return self.club_name

    @classmethod
    def get_members(cls , club):
        return ClubMember.objects.filter(club = club)


class ClubMember(models.Model):
    club = models.ForeignKey(ClubDetails, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='club_memberships')
    
    is_joined = models.BooleanField(default=False)
    role = models.CharField(
        max_length=50, 
        choices=[
            ('Head', 'Head'),
            ('Vice President', 'Vice President'),
            ('Secretary', 'Secretary'),
            ('HOD', 'HOD'),
            ('Associate Professor','Associate Professor'),
            ('Assistant Professor','Assistant Professor'),
            ('Member', 'Member')
        ],
        default='Member'
    )
    power = models.PositiveIntegerField(
        default=1,
        help_text="Assign a numeric value representing the user's power level (higher number = higher power)."
    )

    member_since = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Club Member"
        verbose_name_plural = "Club Members"
        unique_together = ('club', 'user')
        ordering = ['-member_since']
        indexes = [
            models.Index(fields=['club', 'user']),
            models.Index(fields=['power']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.club.club_name}"


class ClubJoinRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey('ClubData', on_delete=models.CASCADE)
    branch_pk = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ], default='Pending')
    request_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - ({self.status})"


