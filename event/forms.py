from django import forms
from .models import Form, Question ,ExtraDetails
from home.models import UserProfile
from django.contrib.auth.models import User


class FormCreateForm(forms.ModelForm):
    created_by = forms.ModelChoiceField(
        queryset=None,
        widget=forms.HiddenInput(),
        required=False
    )

    public = forms.BooleanField()
    class Meta:
        model = Form
        fields = ['form_type', 'title', 'description', 'image', 'created_by']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')  # Pass the current user to the form
        print(user , "in forms")
        super().__init__(*args, **kwargs)
        
        # userUsing=User.objects.filter(pk=usersaved).first()
        self.fields['created_by'].queryset = UserProfile.objects.filter(user=user)
        
        # Set the initial value for created_by to the current user's UserProfile instance
        self.fields['created_by'].initial = UserProfile.objects.get(user=user)


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
