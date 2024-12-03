from django import forms
from .models import Form, Question ,ExtraDetails,  Response
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


# class RegistrationDetailsForm(forms.ModelForm):

#     class Meta:
#         model = Registration_details
#         fields = [
#             'response', 
#             'platform', 
#             'participation_type', 
#             'registration_start', 
#             'registration_end', 
#             'number_of_registration'
#         ]
#         widgets = {
#             'response': forms.HiddenInput(),  # Hide the form field
#             'registration_start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
#             'registration_end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
#             'number_of_registration': forms.NumberInput(attrs={'min': 1, 'step': 1}),
#             'participation_type': forms.Select(attrs={'class': 'form-control'}),
#         }

#     def __init__(self, *args, **kwargs):
#         # Optional: If you want to filter the available forms based on the user
#         user = kwargs.pop('user', None)
#         form_id = kwargs.pop('form_id', None)
#         super().__init__(*args, **kwargs)

#         if form_id:
#             try:
#                 # Fetch the form instance based on the provided form_id
#                 form_instance = Response.objects.get(id=form_id)
#                 self.fields['response'].initial = form_instance  # Set the initial value
#             except Response.DoesNotExist:
#                 raise forms.ValidationError(f"Form with ID {form_id} does not exist.")
