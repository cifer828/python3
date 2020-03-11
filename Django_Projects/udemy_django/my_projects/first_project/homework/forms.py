from django import forms
from homework.models import Users
from django.core import validators


def start_with_z(value):
    if value[0].lower() != 'z':
        raise forms.ValidationError("Must start with z")


class UserForm(forms.ModelForm):
    # create new field which in not in database
    new_first_name = forms.CharField(validators=[start_with_z])

    # add validator to original field
    last_name = forms.CharField(validators=[start_with_z])

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        return last_name[:2]

    class Meta:
        model = Users
        fields = "__all__"

        # other options
        # exclude = ['first_name']
        # fields = ('first_name')


