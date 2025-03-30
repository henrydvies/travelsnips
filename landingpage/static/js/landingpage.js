/**
 * Landing page JavaScript functionality
 * Handles post selection and navigation
 */
document.addEventListener('DOMContentLoaded', function () {
    // View Post button click handler
    const viewPostBtn = document.getElementById('viewPostBtn');
    if (viewPostBtn) {
        viewPostBtn.addEventListener('click', function () {
            const postId = document.getElementById('post_id').value;
            if (postId) {
                window.location.href = `/post/${postId}/`;
            } else {
                alert('Please select a post first.');
            }
        });
    }

    // Create Post button click handler
    const createPostBtn = document.getElementById('createPostBtn');
    if (createPostBtn) {
        createPostBtn.addEventListener('click', function () {
            // Use the createPostUrl variable defined in the template
            window.location.href = createPostUrl;
        });
    }

    // Optional Display icons in the dropdown
    // Optional: Display icons in the dropdown
    const postSelect = document.getElementById('post_id');
    if (postSelect) {
        // Transform the select into a more visual dropdown with icons
        // This is an optional enhancement and would require additional CSS
        const options = postSelect.options;
        for (let i = 0; i < options.length; i++) {
            const iconUrl = options[i].getAttribute('data-icon');
            if (iconUrl) {
                // If using a custom dropdown library, you could display the icon here
                // For a basic implementation, you might just add a class to options with icons
                options[i].classList.add('has-icon');
            }
        }
    }
});