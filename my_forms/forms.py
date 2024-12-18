from django import forms
from .models import Form, ExtraDetails, Registration_details, Notification
from home.models import UserProfile
from django.contrib.auth.models import User
from club.models import ClubMember, ClubDetails



# from ckeditor.widgets import CKEditorWidget  # Import CKEditor widget

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


class FormRegistrationDetailsForm(forms.ModelForm):
    class Meta:
        model = Registration_details
        fields = [
            'form', 
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
            'form': forms.HiddenInput(),  
            'created_by': forms.HiddenInput(),  
            'registration_start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'registration_end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'number_of_registration': forms.NumberInput(attrs={'min': 1, 'step': 1}),
            'participation_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        form_id = kwargs.pop('form_id', None)
        all_clubs_members = kwargs.pop('all_clubs_members', None)
        all_clubs = kwargs.pop('all_clubs', None)
        super().__init__(*args, **kwargs)

        if all_clubs:
            try:
                self.fields['invited_club'].queryset = all_clubs
            except:
                all_clubs = ClubDetails.objects.filter(pk__in=[obj.pk for obj in all_clubs])
                self.fields['invited_club'].queryset = all_clubs

        if form_id:
            try:
                form_instance = Form.objects.get(id=form_id)
                self.fields['form'].initial = form_instance
                print("Form initialized succesfully....")
            except Form.DoesNotExist:
                raise forms.ValidationError(f"Form with ID {form_id} does not exist.")

        # Hide invited_users field initially


    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def save(self, user = None , form = None ,  *args, **kwargs):
        if user:
            self.instance.created_by = user
        if form:
            self.instance.form = form
        return super().save(*args, **kwargs)

# class NotificationForm(forms.ModelForm):
#     class Meta:
#         model = Notification
#         fields = ['title','message', 'status']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#     def clean(self):
#         cleaned_data = super().clean()
#         return cleaned_data
