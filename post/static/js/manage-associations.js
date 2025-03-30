/**
 * Manage post associations JavaScript functionality
 * Handles adding and removing associated people
 */
document.addEventListener('DOMContentLoaded', function () {
    // Get CSRF token
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Add event listeners to all "Add" buttons
    const addButtons = document.querySelectorAll('.btn-add');
    addButtons.forEach(button => {
        button.addEventListener('click', function () {
            const userId = this.getAttribute('data-user-id');
            addAssociatedPerson(userId);
        });
    });

    // Add event listeners to all "Remove" buttons
    const removeButtons = document.querySelectorAll('.btn-remove');
    removeButtons.forEach(button => {
        button.addEventListener('click', function () {
            const userId = this.getAttribute('data-user-id');
            removeAssociatedPerson(userId);
        });
    });

    /**
     * Add a user as an associated person
     */
    function addAssociatedPerson(userId) {
        // Create form data
        const formData = new FormData();
        formData.append('action', 'add');
        formData.append('user_id', userId);

        // Send request
        fetch(manageAssociationsUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            body: formData
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Reload the page to show updated lists
                    window.location.reload();
                } else {
                    showStatus(data.error, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showStatus('An error occurred. Please try again.', 'error');
            });
    }

    /**
     * Remove a user from associated people
     */
    function removeAssociatedPerson(userId) {
        // Create form data
        const formData = new FormData();
        formData.append('action', 'remove');
        formData.append('user_id', userId);

        // Send request
        fetch(manageAssociationsUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            body: formData
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Reload the page to show updated lists
                    window.location.reload();
                } else {
                    showStatus(data.error, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showStatus('An error occurred. Please try again.', 'error');
            });
    }

    /**
     * Show status message
     */
    function showStatus(message, type) {
        const statusEl = document.getElementById('status-message');
        if (statusEl) {
            statusEl.textContent = message;
            statusEl.className = `status-message ${type}`;
            statusEl.style.display = 'block';

            // Hide the message after 3 seconds
            setTimeout(() => {
                statusEl.style.display = 'none';
            }, 3000);
        }
    }
});