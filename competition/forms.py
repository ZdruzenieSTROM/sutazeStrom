from django import forms

class SubmitForm(forms.Form):
    code = forms.CharField(max_length=5)
