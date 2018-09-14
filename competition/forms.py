from functools import reduce

from django import forms

from participant.models import Team

from .models import Event, Problem, Solution

CONTROL = [5, 1, 9, 3, 7]

class SubmitForm(forms.Form):
    event = forms.ModelChoiceField(Event.objects.all(), widget=forms.HiddenInput())
    code = forms.CharField(max_length=6, label='', required=True)

    def __init__(self, *args, **kwargs):
        super(SubmitForm, self).__init__(*args, **kwargs)
        self.fields['code'].widget.attrs.update({'id': 'barcode_input'})

    def clean_code(self):
        try:
            code = [int(c) for c in self.cleaned_data['code']]

        except ValueError:
            raise forms.ValidationError('Nesprávny formát!', code='invalid_format')

        if len(code) != 6:
            raise forms.ValidationError('Nesprávna dĺžka kódu!', code='invalid_length')

        control_digit, code = code[-1], code[:-1]

        if control_digit != reduce(lambda p, n: p + n[0]*n[1], zip(code, CONTROL), 0) % 10:
            raise forms.ValidationError('Neplatný kontrolný súčet!', code='invalid_control_sum')

        return reduce(lambda p, n: p*10 + n, code)

    def clean(self):
        cleaned_data = super(SubmitForm, self).clean()

        if not self.errors:
            code = cleaned_data['code']
            event = cleaned_data['event']

            number, position = code // 100, code % 100

            try:
                team = Team.objects.get(event=event, number=number)
                problem = Problem.objects.get(event=event, position=position)

            except Team.DoesNotExist:
                raise forms.ValidationError('Číslo tímu {} nezodpovedá registrovanému tímu!'.format(number), code='team_does_not_exist')

            except Problem.DoesNotExist:
                raise forms.ValidationError('Úloha číslo {} v tejto súťaži neexistuje!'.format(position), code='problem_does_not_exist')

            else:
                self.cleaned_data['team'] = team
                self.cleaned_data['problem'] = problem

                try:
                    solution = Solution.objects.get(event=event, team=team, problem=problem)

                except:
                    pass

                else:
                    raise forms.ValidationError('Táto úloha už bola odovzdaná v čase {}! ({})'.format(solution.time.strftime('%H:%M:%S (%d. %m. %Y)'), code))

        return cleaned_data

    def save(self):
        return Solution.objects.create(event=self.cleaned_data['event'], team=self.cleaned_data['team'], problem=self.cleaned_data['problem'])
