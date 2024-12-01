from django import forms
from .models import Form, Question ,ExtraDetails
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
