from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def landing_view(request):
    return render(request, 'landingpage/landingpage.html')