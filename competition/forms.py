from django import forms

class SubmitForm(forms.Form):
    code = forms.CharField(max_length=6, label='')

    def __init__(self, *args, **kwargs):
        super(SubmitForm, self).__init__(*args, **kwargs)
        self.fields['code'].widget.attrs.update({'id': 'barcode_input'})
