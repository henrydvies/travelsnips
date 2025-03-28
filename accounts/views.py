from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib import messages

User = get_user_model()

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Basic validation (you can do more robust checks)
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')
        
        # Create the user
        user = User.objects.create_user(username=username, email=email, password=password1)

        # Log the user in automatically (optional)
        login(request, user)
        return redirect('landingpage')
    else:
        # If GET request, just render the registration template
        return render(request, 'accounts/register.html')
