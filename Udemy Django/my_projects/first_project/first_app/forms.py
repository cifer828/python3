from django import forms
from django.core import validators

##################
# form practice
##################
def check_for_z(value):
    if value[0].lower() != 'z':
        raise forms.ValidationError("Initial should be z")


# form without connection to database
class FormName(forms.Form):
    # customize validator
    # name = forms.CharField(validators=[check_for_z])
    name = forms.CharField()
    email = forms.EmailField()
    verify_email = forms.EmailField(label='Enter email again: ')
    # use text area instead of text input
    text = forms.CharField(widget=forms.Textarea)

    # only bot will see this field
    bot_catcher = forms.CharField(required=False,
                                  widget=forms.HiddenInput,
                                  validators=[validators.MaxLengthValidator(0)])
    # !! method name should be clean_xxx, django will automatically process the corresponding field
    # def clean_bot_catcher(self):
    #     boot_catcher = self.cleaned_data['bot_catcher']
    #     if len(boot_catcher) > 0:
    #         raise forms.ValidationError("Gotcha bot!")
    #     return boot_catcher

    # override
    def clean(self):
        all_clean_data = super().clean()
        email = all_clean_data['email']
        vmail = all_clean_data['verify_email']

        if email != vmail:
            raise forms.ValidationError("Two emails are different")


##################
# login and register
##################
from django.contrib.auth.models import User
from first_app.models import UserProfileInfo


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class UserProfileInfoForm(forms.ModelForm):
    class Meta:
        model = UserProfileInfo
        fields = ('portfolio_site', 'profile_pic')