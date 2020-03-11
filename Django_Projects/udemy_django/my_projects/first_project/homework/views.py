from django.shortcuts import render
from django.http import HttpResponse
from homework.models import Users
from homework.forms import UserForm


# Create your views here.
def index(request):
    return HttpResponse("<h1>Welcome</h1> <h2>Go to /users to get more information</h2>")


def users(request):
    user_dict = {'user_dict': Users.objects.all()}
    return render(request, 'homework/users.html', context=user_dict)


def register(request):
    user_form = UserForm()

    if request.method == 'POST':
        user_form = UserForm(request.POST)

        # save input to database
        if user_form.is_valid():
            # change the field
            user_form.cleaned_data['first_name'] = user_form.cleaned_data['first_name']
            user_form.save(commit=True)
            # go back to users page
            return users(request)
        else:
            print("Error: invalid form")

    return render(request, 'homework/register.html', context={'user_form': user_form})
