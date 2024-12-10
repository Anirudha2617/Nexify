from django import forms
from .models import Form, Question ,ExtraDetails,  Response, Registration_details, Notification
from home.models import UserProfile
from django.contrib.auth.models import User


class FormCreateForm(forms.ModelForm):
    public = forms.BooleanField(required=False, initial=False)

    class Meta:
        model = Form
        fields = ['form_type', 'title', 'description', 'image', 'created_by']
        # widgets = {
        #     'created_by': forms.HiddenInput(),  # Hide the created_by field
        # }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Pass the current user to the form
        super().__init__(*args, **kwargs)
        
        if user:  # Check if user is provided
            self.fields['created_by'].initial = user
            print("User updated successfully:", user)
        else:
            print("User not provided")


class FormCreateExtraDetails(forms.ModelForm):
    Model = forms.ModelChoiceField(
        queryset=None,
        widget=forms.HiddenInput(),
        required=False
    )
    class Meta:
        model = ExtraDetails
        fields = ['Model','title','description','image']

    def __init__(self, *args, **kwargs):
        print("Enter the forms")
        formid = kwargs.pop('mainformid')  # Pass the current user to the form
        super().__init__(*args, **kwargs)
        print(Form.objects.get(id = formid))
        self.fields['Model'].queryset = Form.objects.filter(id = formid)
        
        # Set the initial value for created_by to the current user's UserProfile instance
        self.fields['Model'].initial = Form.objects.get(id = formid)


class RegistrationDetailsForm(forms.ModelForm):
    class Meta:
        model = Registration_details
        fields = [
            'response', 
            'platform', 
            'participation_type',
            'minimum_members',
            'maximum_members',
            'registration_start', 
            'registration_end', 
            'number_of_registration',
            'visibility',
            'compulsary',
            'invited_users',
        ]
        widgets = {
            'response': forms.HiddenInput(),  # Hide the form field
            'registration_start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'registration_end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'number_of_registration': forms.NumberInput(attrs={'min': 1, 'step': 1}),
            'participation_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        response_id = kwargs.pop('response_id', None)
        all_clubs_members = kwargs.pop('all_clubs_members', None)
        super().__init__(*args, **kwargs)

        if response_id:
            try:
                form_instance = Response.objects.get(id=response_id)
                self.fields['response'].initial = form_instance
            except Response.DoesNotExist:
                raise forms.ValidationError(f"Form with ID {response_id} does not exist.")

        # Hide invited_users field initially
        if self.initial.get('visibility') == 'public':
            self.fields['invited_users'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        visibility = cleaned_data.get('visibility')
        invited_users = cleaned_data.get('invited_users')

        if visibility != 'Public' and not invited_users:
            raise forms.ValidationError("You must specify invited users if visibility is not public.")

        return cleaned_data


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['title','message', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

from django import forms
from ckeditor.widgets import CKEditorWidget  # Import CKEditor widget
from django import forms
from .models import Response

class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
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
        self.fields['visibility'].choices = Response.VISIBILITY_CHOICES
        self.fields['mode_of_event'].choices = Response.MODE_CHOICES

        # Categories field as CheckboxSelectMultiple
        self.fields['categories'].widget = forms.CheckboxSelectMultiple()

        # Use CKEditor for the about_opportunity field
        self.fields['about_opportunity'].widget = forms.Textarea()

    def get_sub_type_choices(self, opportunity_type):
        if opportunity_type == 'General and case competition':
            return Response.GENERAL_SUB_TYPES
        elif opportunity_type == 'Scholarships':
            return Response.SCHOLARSHIP_SUB_TYPES
        elif opportunity_type == 'Hackathon and coding challenge':
            return Response.HACKATHON_SUB_TYPES
        else:
            return []

    def save(self, user ,  *args, **kwargs):
        self.instance.created_by = user
        return super().save(*args, **kwargs)
        
