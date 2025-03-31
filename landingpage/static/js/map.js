// In a new file: static/js/map.js

document.addEventListener('DOMContentLoaded', function () {
    // Initialize map if the element exists
    const mapElement = document.getElementById('map-view');
    if (mapElement) {
        initMap();
    } else console.log('Map element not found, skipping map initialization.');

    // Map for selecting location when creating/editing posts
    const locationMap = document.getElementById('location-map');
    if (locationMap) {
        initLocationPicker();
    }
});

// Initialize the main map with post pins
function initMap() {
    // Create map centered at an average of all post locations, or default location
    const map = L.map('map-view').setView([0, 0], 2);

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // Fetch post locations from the server
    fetch('/api/post-locations/')
        .then(response => response.json())
        .then(data => {
            // Process post locations data
            const posts = data.posts;
            const bounds = [];

            posts.forEach(post => {
                if (post.latitude && post.longitude) {
                    // Create marker for each post with location
                    const marker = L.marker([post.latitude, post.longitude])
                        .addTo(map);

                    // Create popup with post info and link
                    const popupContent = `
                        <div class="map-popup">
                            <h3>${post.title}</h3>
                            <p>${post.location_name}</p>
                            <a href="/post/${post.id}/" class="btn btn-sm btn-primary">View Post</a>
                        </div>
                    `;
                    marker.bindPopup(popupContent);

                    // Add to bounds for auto-zooming
                    bounds.push([post.latitude, post.longitude]);
                }
            });

            // Zoom map to show all markers if there are any
            if (bounds.length > 0) {
                map.fitBounds(bounds);
            }
        })
        .catch(error => {
            console.error('Error fetching post locations:', error);
        });
}

// Initialize the location picker for creating/editing posts
function initLocationPicker() {
    const map = L.map('location-map').setView([0, 0], 2);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // Try to get user's current location to center the map
    if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                map.setView([position.coords.latitude, position.coords.longitude], 13);
            },
            () => {
                // If geolocation fails, stay at default view
                console.log('Geolocation permission denied');
            }
        );
    }

    // Create a marker that users can drag to select location
    let marker;

    // Check if we're editing a post that already has a location
    const latInput = document.getElementById('edit-latitude') || document.getElementById('latitude');
    const lngInput = document.getElementById('edit-longitude') || document.getElementById('longitude');

    if (latInput.value && lngInput.value) {
        // If editing a post with existing location, place marker there
        const lat = parseFloat(latInput.value);
        const lng = parseFloat(lngInput.value);

        map.setView([lat, lng], 13);
        marker = L.marker([lat, lng], { draggable: true }).addTo(map);
    }

    // Handle map clicks to place/move marker
    map.on('click', function (e) {
        const lat = e.latlng.lat;
        const lng = e.latlng.lng;

        // Update input fields
        latInput.value = lat;
        lngInput.value = lng;

        // Update or create marker
        if (marker) {
            marker.setLatLng(e.latlng);
        } else {
            marker = L.marker(e.latlng, { draggable: true }).addTo(map);
        }

        // Update inputs when marker is dragged
        marker.on('dragend', function () {
            const position = marker.getLatLng();
            latInput.value = position.lat;
            lngInput.value = position.lng;
        });

        // Reverse geocode to get location name (optional)
        const locationNameInput = document.getElementById('edit-location-name') ||
            document.getElementById('location_name');

        if (locationNameInput && !locationNameInput.value) {
            // You can use a service like Nominatim for reverse geocoding
            fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`)
                .then(response => response.json())
                .then(data => {
                    if (data.display_name) {
                        locationNameInput.value = data.display_name;
                    }
                })
                .catch(error => {
                    console.error('Error in reverse geocoding:', error);
                });
        }
    });
}