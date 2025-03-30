from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from post.models import Post

@login_required
def landing_view(request):
    # Get all posts visible to the current user (own posts and linked users' posts)
    posts = request.user.get_all_visible_posts()
    
    if request.method == 'POST':
        # Handle form submission
        post_id = request.POST.get('post_id')
        if post_id:
            # Redirect to the post detail view
            return redirect('post_detail', post_id=post_id)
    
    context = {
        'posts': posts,
    }
    return render(request, 'landingpage/landingpage.html', context)