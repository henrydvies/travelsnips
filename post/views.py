from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post, SubPost, PostAssociation
from django.http import HttpResponseForbidden, HttpResponse, JsonResponse
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def post_detail(request, post_id):
    # Get post and verify the user has access to it
    post = get_object_or_404(Post, id=post_id)
    
    # Check if the user is the owner or has a linked account with the owner
    is_owner = post.owner == request.user
    has_linked_account = request.user in post.owner.get_all_linked_users()
    
    if not (is_owner or has_linked_account):
        return HttpResponseForbidden("You don't have permission to view this post")
    
    # Get all subposts for this post
    subposts = post.subposts.all().order_by('order')
    
    # Get all associated people for this post
    associated_people = post.get_associated_people()
    
    context = {
        'post': post,
        'subposts': subposts,
        'associated_people': associated_people,
        'is_owner': is_owner,
    }
    
    return render(request, 'post/post_detail.html', context)

@login_required
def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        post_icon = request.FILES.get('post_icon')  # Get the uploaded file
        
        # Validate the title
        if title:
            # Create the post
            post = Post.objects.create(
                title=title,
                description=description,
                owner=request.user
            )
            
            # Add the current user as an associated person by default
            post.add_associated_person(request.user)
            
            # Optional save post icon
            if post_icon:
                post.post_icon = post_icon
                post.save()
            
            # Redirect to the post detail page
            return redirect('post_detail', post_id=post.id)
        else:
            # Return an error if no title
            return HttpResponse('Title is required', status=400)
    
    # Get all users who are linked to the current user
    linked_users = request.user.get_all_linked_users()
    
    context = {
        'linked_users': linked_users,
    }
    
    # If not POST, just render the form
    return render(request, 'post/create_post.html', context)

@login_required
def manage_associations(request, post_id):
    """View to add or remove users associated with a post"""
    post = get_object_or_404(Post, id=post_id)
    
    # Only the post owner can manage associations
    if post.owner != request.user:
        return HttpResponseForbidden("Only the post owner can manage associations")
    
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
            
            if action == 'add':
                post.add_associated_person(user)
                return JsonResponse({'success': True, 'message': f'Added {user.username} as an associated person'})
            
            elif action == 'remove':
                post.remove_associated_person(user)
                return JsonResponse({'success': True, 'message': f'Removed {user.username} from associated people'})
            
            else:
                return JsonResponse({'success': False, 'error': 'Invalid action'}, status=400)
            
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
    
    # Get all users who are linked to the current user
    linked_users = request.user.get_all_linked_users()
    
    # Get all users who are already associated with this post
    associated_users = post.get_associated_people()
    
    context = {
        'post': post,
        'linked_users': linked_users,
        'associated_users': associated_users,
    }
    
    return render(request, 'post/manage_associations.html', context)