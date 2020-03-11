from django.shortcuts import render
from first_app.models import Topic, Webpage, AccessRecord
from .forms import FormName, UserForm, UserProfileInfoForm


# login import
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
# for django 1.0 - from django.core.urlresolvers import reverse

# Create your views here.


def index(request):
    return render(request, 'first_app/index.html')


def basics(request):
    # add form from model
    webpages_list = AccessRecord.objects.order_by('date')
    data = {'access_records': webpages_list,
            'text': 'rua',
            'number': 828}

    form = FormName()
    if request.method == 'POST':
        form = FormName(request.POST)
        if form.is_valid():
            print('Validation success!')
            print("Name: " + form.cleaned_data['name'])
            print("Email: " + form.cleaned_data['email'])
            print("Text: " + form.cleaned_data['text'])
    data['form'] = form

    return render(request, "first_app/django-basics.html", context=data)


def register(request):
    registered = False

    # user submits the forms
    if request.method == "POST":
        user_from = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)
        # check validation of both forms
        if user_from.is_valid() and profile_form.is_valid():
            # save() returns a model
            user = user_from.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if "profile_pic" in request.FILES:
                profile.profile_pic = request.FILES['profile_pic']

            profile.save()

            registered = True

        else:
            print(user_from.errors, profile_form.errors)
    # users get empty forms to fill out
    else:
        user_from = UserForm()
        profile_form = UserProfileInfoForm()

    return render(request, 'first_app/register.html',
                  context={"user_form": user_from,
                           "profile_form": profile_form,
                           "registered": registered})


def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # get user
        user = authenticate(username=username, password=password)

        if user:
            # if user is active
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Account not active")
        else:
            # invalid user
            print("login failed")
            print("Username: {} and password {}".format(username, password))
            return render(request, 'first_app/login.html', context={'login_failed': True})

    else:
        return render(request, 'first_app/login.html', context={'login_failed': False})


# use decorator to prevent logout without logging in previously
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


@login_required
def special(request):
    return HttpResponse("You are logged in")