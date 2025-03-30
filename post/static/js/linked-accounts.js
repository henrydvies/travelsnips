/**
 * Linked Accounts JavaScript functionality
 * Handles unlinking accounts
 */
document.addEventListener('DOMContentLoaded', function () {
    // Get CSRF token
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Add event listeners to all "Unlink" buttons
    const unlinkButtons = document.querySelectorAll('.unlink-btn');
    unlinkButtons.forEach(button => {
        button.addEventListener('click', function () {
            const userId = this.getAttribute('data-user-id');
            unlinkAccount(userId);
        });
    });

    /**
     * Unlink an account
     */
    function unlinkAccount(userId) {
        if (!confirm('Are you sure you want to unlink this account?')) {
            return;
        }

        // Create form data
        const formData = new FormData();

        // Send unlink request
        fetch(`${unlinkUrl}${userId}/`, {
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
                    // Remove the user item from the list
                    const userItem = document.querySelector(`.unlink-btn[data-user-id="${userId}"]`).closest('.user-item');
                    userItem.remove();

                    // Show success message
                    showMessage(data.message, 'success');

                    // If no more linked users, show a message
                    const userList = document.querySelector('.user-list');
                    if (userList && userList.children.length === 0) {
                        const emptyMessage = document.createElement('p');
                        emptyMessage.textContent = "You don't have any linked accounts yet.";
                        document.querySelector('.linked-accounts-section').appendChild(emptyMessage);
                    }
                } else {
                    showMessage(data.error, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('An error occurred. Please try again.', 'error');
            });
    }

    /**
     * Show a message
     */
    function showMessage(message, type) {
        const messagesDiv = document.querySelector('.messages');

        if (!messagesDiv) {
            // Create messages div if it doesn't exist
            const newMessagesDiv = document.createElement('div');
            newMessagesDiv.className = 'messages';

            const accountPanel = document.querySelector('.account-panel');
            accountPanel.insertBefore(newMessagesDiv, accountPanel.firstChild);

            showMessage(message, type); // Recursive call now that div exists
            return;
        }

        // Create new message element
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = message;

        // Add to messages div
        messagesDiv.appendChild(messageDiv);

        // Auto remove after 5 seconds
        setTimeout(() => {
            messageDiv.remove();
        }, 5000);
    }
});