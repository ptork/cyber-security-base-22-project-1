from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Profile

# A01:2021 – Broken Access Control
@login_required()
def index(request, profile_id):
  # here we enforce login required but we neglect to check if the 
  # logged on user is the user we're retrieving from the database
  # by changing the parameter in the url a logged in user can see
  # the account details of any other user
  profile = Profile.objects.get(pk=profile_id)
  return render(request, 'index.html', {'profile': profile })

