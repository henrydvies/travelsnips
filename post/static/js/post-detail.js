/**
 * Post Detail JavaScript functionality with editing capabilities
 */
document.addEventListener('DOMContentLoaded', function () {
    // Image gallery functionality
    setupImageGallery();

    // Back to home button functionality
    const backButton = document.getElementById('backButton');
    if (backButton) {
        backButton.addEventListener('click', function () {
            window.location.href = landingPageUrl;
        });
    }

    // Only setup edit mode if user is associated with the post
    if (isAssociated) {
        setupEditMode();
    }

    /**
     * Sets up image gallery with lightbox functionality
     */
    function setupImageGallery() {
        const galleryItems = document.querySelectorAll('.gallery-item img');

        galleryItems.forEach(function (img) {
            img.addEventListener('click', function () {
                // Create lightbox
                const lightbox = document.createElement('div');
                lightbox.className = 'lightbox';

                // Create lightbox image
                const lightboxImg = document.createElement('img');
                lightboxImg.src = this.src;
                lightbox.appendChild(lightboxImg);

                // Create close button
                const closeBtn = document.createElement('span');
                closeBtn.className = 'lightbox-close';
                closeBtn.innerHTML = '&times;';
                lightbox.appendChild(closeBtn);

                // Add lightbox to body
                document.body.appendChild(lightbox);

                // Prevent scrolling when lightbox is open
                document.body.style.overflow = 'hidden';

                // Handle close button click
                closeBtn.addEventListener('click', closeLightbox);

                // Handle click outside image
                lightbox.addEventListener('click', function (e) {
                    if (e.target === lightbox) {
                        closeLightbox();
                    }
                });

                // Handle ESC key
                document.addEventListener('keydown', function (e) {
                    if (e.key === 'Escape') {
                        closeLightbox();
                    }
                });

                function closeLightbox() {
                    document.body.removeChild(lightbox);
                    document.body.style.overflow = '';
                }
            });
        });
    }

    /**
     * Sets up edit mode functionality
     */
    function setupEditMode() {
        const toggleBtn = document.getElementById('toggleEditMode');
        const editPostDetailsBtn = document.getElementById('editPostDetailsBtn');
        const addSubpostBtn = document.getElementById('addSubpostBtn');
        const editSubpostBtns = document.querySelectorAll('.edit-subpost-btn');

        // Get modals
        const editPostModal = document.getElementById('editPostModal');
        const addSubpostModal = document.getElementById('addSubpostModal');
        const editSubpostModal = document.getElementById('editSubpostModal');

        // Get close modal buttons
        const closeButtons = document.querySelectorAll('.close-modal');

        // Toggle edit mode
        if (toggleBtn) {
            toggleBtn.addEventListener('click', function () {
                document.body.classList.toggle('edit-mode');
            });
        }

        // Edit post details button
        if (editPostDetailsBtn) {
            editPostDetailsBtn.addEventListener('click', function (e) {
                e.preventDefault();

                // Get current post details
                fetch(`/post/${postId}/edit/`)
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('edit-title').value = data.title;
                        document.getElementById('edit-description').value = data.description;

                        // Show modal
                        showModal(editPostModal);
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Error loading post details');
                    });
            });
        }

        // Add subpost button
        if (addSubpostBtn) {
            addSubpostBtn.addEventListener('click', function () {
                // Reset form
                document.getElementById('addSubpostForm').reset();
                document.getElementById('subpost-image-preview').innerHTML = '';

                // Show modal
                showModal(addSubpostModal);
            });
        }

        // Edit subpost buttons
        editSubpostBtns.forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                const subpostId = this.getAttribute('data-subpost-id');

                // Get subpost details
                fetch(`/post/subpost/${subpostId}/edit/`)
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('edit-subpost-id').value = data.subpost_id;
                        document.getElementById('edit-subpost-title').value = data.title;
                        document.getElementById('edit-subpost-content').value = data.content;

                        // Populate current images
                        const imagesContainer = document.getElementById('current-images-container');
                        imagesContainer.innerHTML = '';

                        if (data.images.length > 0) {
                            data.images.forEach(image => {
                                const imageItem = document.createElement('div');
                                imageItem.className = 'current-image-item';

                                const img = document.createElement('img');
                                img.src = image.url;
                                img.alt = image.caption || '';

                                const removeBtn = document.createElement('span');
                                removeBtn.className = 'remove-image';
                                removeBtn.innerHTML = '&times;';
                                removeBtn.setAttribute('data-image-id', image.id);
                                removeBtn.addEventListener('click', function () {
                                    this.closest('.current-image-item').remove();
                                });

                                imageItem.appendChild(img);
                                imageItem.appendChild(removeBtn);
                                imagesContainer.appendChild(imageItem);
                            });
                        } else {
                            imagesContainer.innerHTML = '<p>No images for this section.</p>';
                        }

                        // Clear new image preview
                        document.getElementById('edit-subpost-image-preview').innerHTML = '';

                        // Show modal
                        showModal(editSubpostModal);
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Error loading section details');
                    });
            });
        });

        // Close modal buttons
        closeButtons.forEach(function (btn) {
            btn.addEventListener('click', function () {
                const modal = this.closest('.modal');
                if (modal) {
                    modal.style.display = 'none';
                }
            });
        });

        // When clicking outside of modal, close it
        window.addEventListener('click', function (event) {
            if (event.target.classList.contains('modal')) {
                event.target.style.display = 'none';
            }
        });

        // Handle form submissions
        setupFormSubmissions();

        // Setup image previews
        setupImagePreviews();
    }

    /**
     * Sets up form submissions for edit and add actions
     */
    function setupFormSubmissions() {
        // Edit Post Form
        const editPostForm = document.getElementById('editPostForm');
        if (editPostForm) {
            editPostForm.addEventListener('submit', function (e) {
                e.preventDefault();

                const formData = new FormData(editPostForm);

                // Send update request
                fetch(`/post/${postId}/edit/`, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // Close modal
                            document.getElementById('editPostModal').style.display = 'none';

                            // Reload the page to show changes
                            window.location.reload();
                        } else {
                            alert(data.error || 'Error updating post');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Error updating post');
                    });
            });
        }

        // Add Subpost Form
        const addSubpostForm = document.getElementById('addSubpostForm');
        if (addSubpostForm) {
            addSubpostForm.addEventListener('submit', function (e) {
                e.preventDefault();

                const formData = new FormData(addSubpostForm);

                // Send create request
                fetch(`/post/${postId}/add-subpost/`, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // Close modal
                            document.getElementById('addSubpostModal').style.display = 'none';

                            // Reload the page to show changes
                            window.location.reload();
                        } else {
                            alert(data.error || 'Error adding section');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Error adding section');
                    });
            });
        }

        // Edit Subpost Form
        const editSubpostForm = document.getElementById('editSubpostForm');
        if (editSubpostForm) {
            editSubpostForm.addEventListener('submit', function (e) {
                e.preventDefault();

                const formData = new FormData(editSubpostForm);
                const subpostId = document.getElementById('edit-subpost-id').value;

                // Add any image IDs to remove
                const removeBtns = document.querySelectorAll('.remove-image');
                removeBtns.forEach(function (btn) {
                    const imageId = btn.getAttribute('data-image-id');
                    const item = btn.closest('.current-image-item');

                    if (item.style.display === 'none' || !item.parentNode) {
                        formData.append('remove_images', imageId);
                    }
                });

                // Send update request
                fetch(`/post/subpost/${subpostId}/edit/`, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // Close modal
                            document.getElementById('editSubpostModal').style.display = 'none';

                            // Reload the page to show changes
                            window.location.reload();
                        } else {
                            alert(data.error || 'Error updating section');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Error updating section');
                    });
            });
        }
    }

    /**
     * Sets up image preview functionality
     */
    function setupImagePreviews() {
        // Post icon preview
        const postIconInput = document.getElementById('edit-post-icon');
        const postIconPreview = document.getElementById('edit-image-preview');

        if (postIconInput && postIconPreview) {
            postIconInput.addEventListener('change', function () {
                previewImages(this.files, postIconPreview, true);
            });
        }

        // Subpost images preview
        const subpostImagesInput = document.getElementById('subpost-images');
        const subpostImagesPreview = document.getElementById('subpost-image-preview');

        if (subpostImagesInput && subpostImagesPreview) {
            subpostImagesInput.addEventListener('change', function () {
                previewImages(this.files, subpostImagesPreview);
            });
        }

        // Edit subpost images preview
        const editSubpostImagesInput = document.getElementById('edit-subpost-images');
        const editSubpostImagesPreview = document.getElementById('edit-subpost-image-preview');

        if (editSubpostImagesInput && editSubpostImagesPreview) {
            editSubpostImagesInput.addEventListener('change', function () {
                previewImages(this.files, editSubpostImagesPreview);
            });
        }
    }

    /**
     * Preview selected images
     */
    function previewImages(files, container, singleImage = false) {
        // Clear preview container
        container.innerHTML = '';

        if (files.length > 0) {
            // Create grid container for multiple images
            const grid = document.createElement('div');
            grid.className = 'image-preview-grid';
            container.appendChild(grid);

            // Preview each image
            for (let i = 0; i < files.length; i++) {
                const file = files[i];

                // Only process image files
                if (!file.type.match('image.*')) {
                    continue;
                }

                const reader = new FileReader();
                reader.onload = function (e) {
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.className = singleImage ? 'icon-preview' : 'preview-thumbnail';

                    if (singleImage) {
                        container.innerHTML = '';
                        container.appendChild(img);
                    } else {
                        const imgContainer = document.createElement('div');
                        imgContainer.className = 'preview-item';
                        imgContainer.appendChild(img);
                        grid.appendChild(imgContainer);
                    }
                };

                reader.readAsDataURL(file);

                // For single image preview, only process the first file
                if (singleImage) {
                    break;
                }
            }
        }
    }

    /**
     * Shows a modal dialog
     */
    function showModal(modal) {
        if (modal) {
            modal.style.display = 'block';
        }
    }
});