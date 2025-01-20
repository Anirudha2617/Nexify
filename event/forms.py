from django import forms
from .models import Event, Registration_details, Notification
from home.models import UserProfile
from django.contrib.auth.models import User
from club.models import ClubMember, ClubDetails



# from django import forms
# from ckeditor.widgets import CKEditorWidget  # Import CKEditor widget
# from django import forms
# from .models import Event

from django import forms
from django.utils.dateparse import parse_datetime
from django.core.exceptions import ValidationError
from datetime import datetime

class EventCreateForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['created_by', 
                  'logo', 
                  'opportunity_type', 
                  'opportunity_sub_type', 
                  'visibility', 
                  'event_start',
                  'event_end',
                  'opportunity_title', 
                  'organization', 
                  'mode_of_event', 
                  'categories', 
                  'skills_to_be_assessed', 
                  'about_opportunity', 
                  'website_url', 
                  'festival_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.opportunity_type:
            self.fields['opportunity_sub_type'].choices = self.get_sub_type_choices(self.instance.opportunity_type)

        self.fields['visibility'].widget = forms.RadioSelect()
        self.fields['mode_of_event'].widget = forms.RadioSelect()

        self.fields['visibility'].choices = Event.VISIBILITY_CHOICES
        self.fields['mode_of_event'].choices = Event.MODE_CHOICES

        self.fields['categories'].widget = forms.CheckboxSelectMultiple()
        self.fields['about_opportunity'].widget = forms.Textarea()

        # Format the instance data for the datetime-local input
        if self.instance and self.instance.event_start:
            self.fields['event_start'].widget.attrs['value'] = self.instance.event_start.strftime('%Y-%m-%dT%H:%M')
        if self.instance and self.instance.event_end:
            self.fields['event_end'].widget.attrs['value'] = self.instance.event_end.strftime('%Y-%m-%dT%H:%M')

        self.fields['event_start'].widget = forms.TextInput(
            attrs={
                'placeholder': 'YYYY-MM-DDTHH:MM',
                'type': 'datetime-local',
            }
        )
        self.fields['event_end'].widget = forms.TextInput(
            attrs={
                'placeholder': 'YYYY-MM-DDTHH:MM',
                'type': 'datetime-local',
            }
        )


    def get_sub_type_choices(self, opportunity_type):
        if opportunity_type == 'General and case competition':
            return Event.GENERAL_SUB_TYPES
        elif opportunity_type == 'Scholarships':
            return Event.SCHOLARSHIP_SUB_TYPES
        elif opportunity_type == 'Hackathon and coding challenge':
            return Event.HACKATHON_SUB_TYPES
        else:
            return []

    def clean(self):
        cleaned_data = super().clean()

        event_start = cleaned_data.get('event_start')
        event_end = cleaned_data.get('event_end')

        # Parse the datetime fields if they are strings
        if isinstance(event_start, str):
            event_start = parse_datetime(event_start)
            if not event_start:
                raise ValidationError({'event_start': 'Invalid start date format. Use YYYY-MM-DDTHH:MM.'})
            cleaned_data['event_start'] = event_start

        if isinstance(event_end, str):
            event_end = parse_datetime(event_end)
            if not event_end:
                raise ValidationError({'event_end': 'Invalid end date format. Use YYYY-MM-DDTHH:MM.'})
            cleaned_data['event_end'] = event_end

        # Validate that start date is before end date
        if event_start and event_end and event_start >= event_end:
            raise ValidationError({'event_end': 'End date must be after the start date.'})

        return cleaned_data

    def save(self, user, *args, **kwargs):
        self.instance.created_by = user
        return super().save(*args, **kwargs)

        
class RegistrationDetailsForm(forms.ModelForm):
    class Meta:
        model = Registration_details
        fields = [
            'event', 
            'platform', 
            'participation_type',
            'minimum_members',
            'maximum_members',
            'registration_start', 
            'registration_end', 
            'number_of_registration',
            'compulsary',
            'visibility',
            'invited_club',
            'invited_users',

        ]
        widgets = {

            'event': forms.HiddenInput(),  # Hide the form field
            'registration_start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'registration_end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'number_of_registration': forms.NumberInput(attrs={'min': 1, 'step': 1}),
            'participation_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        response_id = kwargs.pop('response_id', None)
        all_clubs_members = kwargs.pop('all_clubs_members', None)
        all_clubs = kwargs.pop('all_clubs', None)
        super().__init__(*args, **kwargs)

        if all_clubs:
            try:
                self.fields['invited_club'].queryset = all_clubs
            except :
                all_clubs = ClubDetails.objects.filter(pk__in=[obj.pk for obj in all_clubs])
                self.fields['invited_club'].queryset = all_clubs

        if response_id:
            try:
                form_instance = Event.objects.get(id=response_id)
                self.fields['event'].initial = form_instance
            except Event.DoesNotExist:
                raise forms.ValidationError(f"Form with ID {response_id} does not exist.")

        # Hide invited_users field initially
        if self.initial.get('visibility') == 'public':
            self.fields['invited_users'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()

        return cleaned_data





# forms.py
from django.forms import modelformset_factory
from .models import Timeline

class TimelineForm(forms.ModelForm):
    class Meta:
        model = Timeline
        fields = ['date', 'event']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

# Formset for multiple timelines
TimelineFormSet = modelformset_factory(
    Timeline,
    form=TimelineForm,
    extra=3,  # Number of empty forms to display
    can_delete=True  # Allow deletion of existing timelines
)



