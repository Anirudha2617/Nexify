from .models import Team
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django import forms
from .models import Team, Event

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['team_name', 'leader', 'created_by', 'invited_users', 'event']
        widgets = {
            'event': forms.HiddenInput(),
            'created_by': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        event_id = kwargs.pop('event_id', None)  # Event ID passed explicitly
        leader = kwargs.pop('leader', None)  # Current leader (User object)
        super().__init__(*args, **kwargs)

        # Set the event field's initial value
        if event_id:
            event_instance = Event.objects.get(id=event_id)
            self.fields['event'].initial = event_instance

        # Update the queryset for the leader field to include the current leader and team members
        if leader and self.instance.pk:
            # If the form is editing an existing team, include all current members and the leader
            current_members = self.instance.accepted_users.all()
            leader_queryset = User.objects.filter(pk__in=current_members.values_list('pk', flat=True)) | User.objects.filter(pk=leader.pk)
        else:
            # For a new team, limit the leader to the current user
            leader_queryset = User.objects.filter(pk=leader.pk)

        self.fields['leader'].queryset = leader_queryset
        self.fields['leader'].initial = leader

        # Set the created_by field to the leader
        self.fields['created_by'].queryset = leader_queryset
        self.fields['created_by'].initial = leader

        # Set the invited_users queryset to exclude those already in teams
        if event_id:
            form_event_instance = Event.objects.get(id=event_id)
            self.fields['invited_users'].queryset = Team.not_in_any_team(form_event_instance)

    def save(self, *args, **kwargs):
        # Ensure the event field is set correctly
        self.instance.event = self.fields['event'].initial
        return super().save(*args, **kwargs)
