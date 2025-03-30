/**
 * Post Detail JavaScript functionality
 * Handles interactions on the post detail page
 */
document.addEventListener('DOMContentLoaded', function () {
    // Image gallery functionality
    setupImageGallery();

    // Back to home button functionality
    const backButton = document.getElementById('backButton');
    if (backButton) {
        backButton.addEventListener('click', function () {
            // Use the landingPageUrl variable defined in the template
            window.location.href = landingPageUrl;
        });
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
});