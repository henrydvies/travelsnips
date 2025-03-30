from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post, SubPost
from django.http import HttpResponseForbidden
from django.http import HttpResponse

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    subposts = post.subposts.all().order_by('order')
    
    context = {
        'post': post,
        'subposts': subposts,
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
            
            # Optional save post icon
            if post_icon:
                post.post_icon = post_icon
                post.save()
            
            # Redirect to the post detail page
            return redirect('post_detail', post_id=post.id)
        else:
            # Return an error if no title
            return HttpResponse('Title is required', status=400)
    
    # If not POST, just render the form
    return render(request, 'post/create_post.html')