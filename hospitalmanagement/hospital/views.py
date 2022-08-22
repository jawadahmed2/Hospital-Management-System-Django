from django.shortcuts import render,redirect,reverse
from django.http import HttpResponseRedirect

# Create your views here.

# View for home page
def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/index.html')
