document.addEventListener('DOMContentLoaded', function () {
    // Mobile menu toggle
    const menuToggle = document.getElementById('mobile-menu-toggle');
    const navbarContent = document.getElementById('navbarContent');

    if (menuToggle && navbarContent) {
        menuToggle.addEventListener('click', function () {
            navbarContent.classList.toggle('show');
        });
    }

    // Close the menu when clicking outside
    document.addEventListener('click', function (event) {
        if (!event.target.closest('.navbar') && navbarContent && navbarContent.classList.contains('show')) {
            navbarContent.classList.remove('show');
        }
    });
});