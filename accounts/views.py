from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse 

User = get_user_model()

def register_view(request):
    if request.method == 'POST':
        # Check if this is an AJAX request 
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':  
            import json  
            data = json.loads(request.body)  
            username = data.get('username')  
            email = data.get('email')  
            password1 = data.get('password1')  
            password2 = data.get('password2')  
        else:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

        # Basic validation
        if password1 != password2:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':  
                
                return JsonResponse({'success': False, 'error': 'Passwords do not match.'}, status=400)  
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':  
                
                return JsonResponse({'success': False, 'error': 'Username already exists.'}, status=400)  
            messages.error(request, "Username already exists.")
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':  
                
                return JsonResponse({'success': False, 'error': 'Email already exists.'}, status=400)  
            messages.error(request, "Email already exists.")
            return redirect('register')
        
        if len(password1) < 6:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':  
                
                return JsonResponse({'success': False, 'error': 'Password must be at least 6 characters long.'}, status=400)  
            messages.error(request, "Password must be at least 6 characters long.")
            return redirect('register')
        
        # Create the user (password hashing is handled automatically) 
        user = User.objects.create_user(username=username, email=email, password=password1)  
        login(request, user)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':  
            
            return JsonResponse({'success': True, 'redirect_url': '/landingpage/landingpage'})  
        return redirect('landingpage')
    else:
        return render(request, 'accounts/register.html')


def login_view(request):
    if request.method == 'POST':
        # Check if this is an AJAX request 
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':  
            import json  
            data = json.loads(request.body)  
            username = data.get('username')  
            password = data.get('password')  
            user = authenticate(request, username=username, password=password)  
            if user is not None:
                login(request, user)
                
                return JsonResponse({'success': True, 'redirect_url': '/landingpage/landingpage'})  
            else:
                
                return JsonResponse({'success': False, 'error': 'Invalid username or password.'}, status=400)  
        else:
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                return redirect('landingpage')
            else:
                return render(request, 'accounts/login.html', {'form': form})
    else:
        form = AuthenticationForm(request)
    return render(request, 'accounts/login.html', {'form': form})
