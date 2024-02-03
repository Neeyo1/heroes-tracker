from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, "heroes_tracker/index.html")

def testing_page(request, clan_name):
    return render(request, "heroes_tracker/testing_page.html", {"clan_name": clan_name})
