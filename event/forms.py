from django import forms
from .models import Event, Registration_details, Notification
from home.models import UserProfile
from django.contrib.auth.models import User
from club.models import ClubMember, ClubDetails



# from django import forms
# from ckeditor.widgets import CKEditorWidget  # Import CKEditor widget
# from django import forms
# from .models import Event

class EventCreateForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['created_by', 'logo', 'opportunity_type', 'opportunity_sub_type', 'visibility', 'opportunity_title', 'organization', 'mode_of_event', 'categories', 'skills_to_be_assessed', 'about_opportunity', 'website_url', 'festival_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamically update the choices for opportunity_sub_type based on opportunity_type
        if self.instance and self.instance.opportunity_type:
            self.fields['opportunity_sub_type'].choices = self.get_sub_type_choices(self.instance.opportunity_type)

        # Set visibility and mode_of_event widgets to radio buttons
        self.fields['visibility'].widget = forms.RadioSelect()
        self.fields['mode_of_event'].widget = forms.RadioSelect()

        # Update choices for visibility and mode_of_event
        self.fields['visibility'].choices = Event.VISIBILITY_CHOICES
        self.fields['mode_of_event'].choices = Event.MODE_CHOICES

        # Categories field as CheckboxSelectMultiple
        self.fields['categories'].widget = forms.CheckboxSelectMultiple()

        # Use CKEditor for the about_opportunity field
        self.fields['about_opportunity'].widget = forms.Textarea()

    def get_sub_type_choices(self, opportunity_type):
        if opportunity_type == 'General and case competition':
            return Event.GENERAL_SUB_TYPES
        elif opportunity_type == 'Scholarships':
            return Event.SCHOLARSHIP_SUB_TYPES
        elif opportunity_type == 'Hackathon and coding challenge':
            return Event.HACKATHON_SUB_TYPES
        else:
            return []

    def save(self, user ,  *args, **kwargs):
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

# class NotificationForm(forms.ModelForm):
#     class Meta:
#         model = Notification
#         fields = ['title','message', 'status']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#     def clean(self):
#         cleaned_data = super().clean()
#         return cleaned_data


# # function toggleInvitedUsersField() {
# #     if (visibilityField.value === "Public") {
# #         invitedUsersFieldWrapper.addClass('hidden');
# #         invitedUsersField.val(null).trigger('change'); // Clear selection
# #     } else {
# #         invitedUsersFieldWrapper.removeClass('hidden');
# #     }
# # }
# # // Initial state
# # toggleInvitedUsersField();
# # // Update on change
# # visibilityField.addEventListener("change", toggleInvitedUsersField);