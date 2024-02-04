from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from .models import MapGroup, Map, Hero
from .forms import MapGroupForm, MapForm, HeroForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse

# Create your views here.
def index(request):
    return render(request, "heroes_tracker/index.html")

def testing_page(request, clan_name):
    return render(request, "heroes_tracker/testing_page.html", {"clan_name": clan_name})

def login_to_page(request):
    context = {}
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            print("Success")
            next_url = request.GET.get('next') or reverse('index')
            return HttpResponseRedirect(next_url)
        else:
            error_message = "Incorrect login or password"
            context["error_message"] = error_message
            return render(request, "heroes_tracker/login_form.html", context)
    return render(request, "heroes_tracker/login_form.html", context)

def logout_from_page(request):
    logout(request)
    next_url = request.GET.get('next') or reverse('index')
    return HttpResponseRedirect(next_url)

def register_to_page(request):
    context = {}
    form = UserCreationForm()
    context["form"] = form
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            error_message = "Error during registration"
            context["error_message"] = error_message
            context["form"] = form
            return render(request, "heroes_tracker/register_form.html", context)
    return render(request, "heroes_tracker/register_form.html", context)