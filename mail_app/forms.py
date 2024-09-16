from django import forms
from .models import MailAccount


class MailAccountForm(forms.ModelForm):
    # start_listener = forms.BooleanField(
    #     required=True, initial=True, widget=forms.HiddenInput)

    class Meta:
        model = MailAccount
        fields = ['email', 'password']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'id': 'floatingInput',
                'placeholder': 'Введите почту'
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'form-control',
                'id': 'floatingPassword',
                'placeholder': 'Введите пароль'
            })
        }
