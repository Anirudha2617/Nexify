from django import forms

class GitHubUserForm(forms.Form):
    username = forms.CharField(max_length=100, label="GitHub Username")
