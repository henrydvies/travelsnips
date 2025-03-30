/**
 * Create Post JavaScript functionality
 * Handles form submission and validation for creating new posts
 */
document.addEventListener('DOMContentLoaded', function () {
    // Image preview functionality
    const postIconInput = document.getElementById('post_icon');
    const imagePreview = document.getElementById('image-preview');

    if (postIconInput) {
        postIconInput.addEventListener('change', function () {
            // Clear previous preview
            imagePreview.innerHTML = '';

            if (this.files && this.files[0]) {
                const file = this.files[0];

                // Only process image files
                if (!file.type.match('image.*')) {
                    return;
                }

                const reader = new FileReader();

                reader.onload = function (e) {
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.className = 'icon-preview';
                    imagePreview.appendChild(img);
                };

                reader.readAsDataURL(file);
            }
        });
    }


    // Submit button click handler
    const submitBtn = document.getElementById('submitBtn');
    if (submitBtn) {
        submitBtn.addEventListener('click', function () {
            const title = document.getElementById('title').value;
            const description = document.getElementById('description').value;

            if (!title) {
                showStatus('Please enter a title for your post.', 'error');
                return;
            }

            // Get CSRF token
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            // Display loading state
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="loading"></span>Creating...';

            // Create form data object (standard form submission instead of JSON)
            const formData = new FormData();
            formData.append('title', title);
            formData.append('description', description);

            // Only append file if one was selected
            if (iconFile) {
                formData.append('post_icon', iconFile);
            }

            // Send form data to server
            console.log('Submitting form data:', window.location.pathname); // Debugging line
            fetch(window.location.pathname, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken
                },
                body: formData
            })
                .then(response => {
                    if (response.redirected) {
                        // If the server redirected us, follow the redirect
                        window.location.href = response.url;
                    } else if (!response.ok) {
                        throw new Error('Network response was not ok');
                    } else {
                        // If no redirect but response is ok, go to landing page
                        window.location.href = '/landingpage/landingpage';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    resetSubmitButton();
                    showStatus('An error occurred. Please try again.', 'error');
                });
        });
    }

    // Cancel button click handler
    const cancelBtn = document.getElementById('cancelBtn');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', function () {
            window.location.href = '/landingpage/landingpage';
        });
    }

    // Helper function to show status messages
    function showStatus(message, type) {
        const statusEl = document.getElementById('status-message');
        if (statusEl) {
            statusEl.textContent = message;
            statusEl.className = `status-message ${type}`;
            statusEl.style.display = 'block';
        }
    }

    // Helper function to reset the submit button
    function resetSubmitButton() {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Create Post';
        }
    }
});