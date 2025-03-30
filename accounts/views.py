from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse 
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404

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

@login_required
def link_request_view(request, user_id):
    """View to create a link with another user"""
    target_user = get_object_or_404(User, id=user_id)
    
    # Don't allow linking to self
    if target_user == request.user:
        messages.error(request, "You cannot link to your own account.")
        return redirect('linked_accounts')
    
    # Check if link already exists
    existing_link = LinkedAccount.objects.filter(
        (models.Q(user1=request.user) & models.Q(user2=target_user)) |
        (models.Q(user1=target_user) & models.Q(user2=request.user))
    ).first()
    
    if existing_link:
        if existing_link.is_active:
            messages.info(request, f"You are already linked with {target_user.username}.")
        else:
            # Reactivate the link if it exists but is inactive
            existing_link.is_active = True
            existing_link.save()
            messages.success(request, f"Your link with {target_user.username} has been reactivated.")
    else:
        # Create a new link
        try:
            link = LinkedAccount(user1=request.user, user2=target_user)
            link.save()
            messages.success(request, f"Successfully linked with {target_user.username}.")
        except Exception as e:
            messages.error(request, f"Error creating link: {str(e)}")
    
    return redirect('linked_accounts')

@login_required
def linked_accounts_view(request):
    """View to manage linked accounts"""
    # Get all active links for the current user
    user_links = LinkedAccount.objects.filter(
        models.Q(user1=request.user) | models.Q(user2=request.user),
        is_active=True
    )
    
    # Extract the linked users from these links
    linked_users = []
    for link in user_links:
        if link.user1 == request.user:
            linked_users.append(link.user2)
        else:
            linked_users.append(link.user1)
    
    # Handle search for new users to link
    search_results = []
    search_query = request.GET.get('search', '')
    
    if search_query:
        # Find users matching the search query who are not already linked
        search_results = User.objects.filter(
            username__icontains=search_query
        ).exclude(
            id=request.user.id
        ).exclude(
            id__in=[user.id for user in linked_users]
        )[:10]  # Limit to 10 results
    
    context = {
        'linked_users': linked_users,
        'search_results': search_results,
        'search_query': search_query,
    }
    
    return render(request, 'accounts/linked_accounts.html', context)



@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def unlink_account_view(request, user_id):
    """View to remove a link with another user"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)
    
    target_user = get_object_or_404(User, id=user_id)
    
    # Find the link
    link = LinkedAccount.objects.filter(
        (models.Q(user1=request.user) & models.Q(user2=target_user)) |
        (models.Q(user1=target_user) & models.Q(user2=request.user)),
        is_active=True
    ).first()
    
    if not link:
        return JsonResponse({'success': False, 'error': 'Link not found'}, status=404)
    
    # Deactivate the link instead of deleting
    link.is_active = False
    link.save()
    
    return JsonResponse({'success': True, 'message': f"Unlinked from {target_user.username}"})