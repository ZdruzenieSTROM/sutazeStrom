from functools import reduce

from django import forms
from django.core.exceptions import ValidationError

CONTROL = [5, 1, 9, 3, 7]

class SubmitForm(forms.Form):
    code = forms.CharField(max_length=6, label='', required=True)

    def __init__(self, *args, **kwargs):
        super(SubmitForm, self).__init__(*args, **kwargs)
        self.fields['code'].widget.attrs.update({'id': 'barcode_input'})

    def clean_code(self):
        try:
            code = [int(c) for c in self.cleaned_data['code']]

        except ValueError:
            raise ValidationError('Nesprávny formát!', code='invalid_format')

        if len(code) != 6:
            raise ValidationError('Nesprávna dĺžka kódu!', code='invalid_length')

        control_digit, code = code[-1], code[:-1]

        if control_digit != reduce(lambda p, n: p + n[0]*n[1], zip(code, CONTROL), 0) % 10:
            raise ValidationError('Neplatný kontrolný súčet!', code='invalid_control_sum')

        return code
