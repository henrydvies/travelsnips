from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post, SubPost, PostAssociation, PostImage
from django.http import HttpResponseForbidden, HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
from django.db.models import Max

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
    
    # Check if the current user is associated with this post
    is_associated = request.user in associated_people
    
    context = {
        'post': post,
        'subposts': subposts,
        'associated_people': associated_people,
        'is_owner': is_owner,
        'is_associated': is_associated,  # Added this for edit functionality
    }
    
    return render(request, 'post/post_detail.html', context)

@login_required
def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        post_icon = request.FILES.get('post_icon')
        
        # Get location data
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        location_name = request.POST.get('location_name', '')
        
        # Validate the title
        if title:
            # Create the post
            post = Post.objects.create(
                title=title,
                description=description,
                owner=request.user,
                location_name=location_name
            )
            
            # Set location coordinates if provided
            if latitude and longitude:
                post.latitude = float(latitude)
                post.longitude = float(longitude)
                post.save()
            
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

@login_required
def edit_post(request, post_id):
    """View to edit post details"""
    post = get_object_or_404(Post, id=post_id)
    
    # Check if the user is associated with this post
    if request.user not in post.get_associated_people():
        return HttpResponseForbidden("You don't have permission to edit this post")
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        post_icon = request.FILES.get('post_icon')
        
        # Update post fields if values provided
        if title:
            post.title = title
        if description:
            post.description = description
        if post_icon:
            post.post_icon = post_icon
        
        post.save()
        
        return JsonResponse({'success': True, 'message': 'Post updated successfully'})
    
    # For GET requests, return a JSON response with the current post details
    return JsonResponse({
        'post_id': post.id,
        'title': post.title,
        'description': post.description,
        'has_icon': bool(post.post_icon)
    })

@login_required
def add_subpost(request, post_id):
    """View to add a new subpost to a post"""
    post = get_object_or_404(Post, id=post_id)
    
    # Check if the user is associated with this post
    if request.user not in post.get_associated_people():
        return HttpResponseForbidden("You don't have permission to add content to this post")
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content', '')
        
        if not title:
            return JsonResponse({'success': False, 'error': 'Title is required'}, status=400)
        
        # Determine the order (place it at the end)
        order = SubPost.objects.filter(post=post).count()
        
        # Create the new subpost
        subpost = SubPost.objects.create(
            post=post,
            subpost_title=title,
            content=content,
            order=order
        )
        
        # Process images if any
        images = request.FILES.getlist('images')
        for i, image in enumerate(images):
            # Get caption for this image
            caption = request.POST.get(f'image_caption_{i}', '')
            
            PostImage.objects.create(
                subpost=subpost,
                image=image,
                caption=caption,
                order=i
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Content added successfully',
            'subpost_id': subpost.id
        })
    
    # For GET requests, just render the form
    return render(request, 'post/add_subpost.html', {
        'post': post
    })

@login_required
def edit_subpost(request, subpost_id):
    """View to edit an existing subpost"""
    subpost = get_object_or_404(SubPost, id=subpost_id)
    post = subpost.post
    
    # Check if the user is associated with this post
    if request.user not in post.get_associated_people():
        return HttpResponseForbidden("You don't have permission to edit this content")
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content', '')
        
        if not title:
            return JsonResponse({'success': False, 'error': 'Title is required'}, status=400)
        
        # Update subpost fields
        subpost.subpost_title = title
        subpost.content = content
        subpost.save()
        
        # Process new images if any
        new_images = request.FILES.getlist('new_images')
        for i, image in enumerate(new_images):
            # Get the current highest order
            highest_order = PostImage.objects.filter(subpost=subpost).aggregate(Max('order'))['order__max'] or -1
            
            # Get caption for this image
            caption = request.POST.get(f'image_caption_{i}', '')
            
            PostImage.objects.create(
                subpost=subpost,
                image=image,
                caption=caption,
                order=highest_order + 1 + i
            )
        
        # Remove images if requested
        images_to_remove = request.POST.getlist('remove_images')
        if images_to_remove:
            PostImage.objects.filter(id__in=images_to_remove).delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Content updated successfully'
        })
    
    # For GET requests, return details of this subpost
    images = [{'id': img.id, 'url': img.image.url, 'caption': img.caption} 
              for img in subpost.images.all().order_by('order')]
    
    return JsonResponse({
        'subpost_id': subpost.id,
        'title': subpost.subpost_title,
        'content': subpost.content,
        'images': images
    })



# In post/views.py
@login_required
def post_locations(request):
    """API endpoint to get post locations for the map"""
    # Get all posts visible to the current user
    visible_posts = request.user.get_all_visible_posts()
    
    # Filter posts with location data and serialize the data
    posts_with_location = [
        {
            'id': post.id,
            'title': post.title,
            'latitude': post.latitude,
            'longitude': post.longitude,
            'location_name': post.location_name,
            'icon': post.post_icon.url if post.post_icon else None
        }
        for post in visible_posts
        if post.latitude and post.longitude
    ]
    
    return JsonResponse({'posts': posts_with_location})