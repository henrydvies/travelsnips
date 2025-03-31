/**
 * Map functionality for TravelSnips
 * Handles both the global map view and location picker for creating/editing posts
 */
document.addEventListener('DOMContentLoaded', function () {
    console.log('Map.js loaded');

    // Initialize map if the element exists
    const mapElement = document.getElementById('map-view');
    if (mapElement) {
        console.log('Initializing main map view');
        initMap();
    }

    // Map for selecting location when creating/editing posts
    const locationMap = document.getElementById('location-map');
    if (locationMap) {
        console.log('Initializing location picker');
        initLocationPicker();
    }
});

// Initialize the main map with post pins
function initMap() {
    // Create map centered at a default location
    const map = L.map('map-view').setView([20, 0], 2);

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Fetch post locations from the server
    fetch('/post/api/post-locations/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            console.log('Received post locations:', data);
            const posts = data.posts;
            const bounds = [];

            if (posts && posts.length > 0) {
                posts.forEach(post => {
                    if (post.latitude && post.longitude) {
                        // Create marker for each post with location
                        const marker = L.marker([post.latitude, post.longitude])
                            .addTo(map);

                        // Create popup with post info and link
                        const popupContent = `
                            <div class="map-popup">
                                <h3>${post.title}</h3>
                                <p>${post.location_name || 'No location name'}</p>
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
            } else {
                console.log('No posts with locations found');
            }
        })
        .catch(error => {
            console.error('Error fetching post locations:', error);
        });
}

// Initialize the location picker for creating/editing posts
function initLocationPicker() {
    const map = L.map('location-map').setView([20, 0], 2);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Try to get user's current location to center the map
    if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                console.log('Got user location');
                map.setView([position.coords.latitude, position.coords.longitude], 13);
            },
            (error) => {
                // If geolocation fails, stay at default view
                console.log('Geolocation error:', error);
            }
        );
    } else {
        console.log('Geolocation not available');
    }

    // Create a marker that users can drag to select location
    let marker;

    // Check if we're editing a post that already has a location
    const latInput = document.getElementById('edit-latitude') || document.getElementById('latitude');
    const lngInput = document.getElementById('edit-longitude') || document.getElementById('longitude');

    if (latInput && lngInput && latInput.value && lngInput.value) {
        // If editing a post with existing location, place marker there
        const lat = parseFloat(latInput.value);
        const lng = parseFloat(lngInput.value);

        console.log('Setting initial location:', lat, lng);
        map.setView([lat, lng], 13);
        marker = L.marker([lat, lng], { draggable: true }).addTo(map);

        // Handle marker drag
        marker.on('dragend', function () {
            const position = marker.getLatLng();
            latInput.value = position.lat;
            lngInput.value = position.lng;
            console.log('Marker dragged to:', position.lat, position.lng);
        });
    }

    // Handle map clicks to place/move marker
    map.on('click', function (e) {
        const lat = e.latlng.lat;
        const lng = e.latlng.lng;
        console.log('Map clicked at:', lat, lng);

        // Update input fields
        if (latInput && lngInput) {
            latInput.value = lat;
            lngInput.value = lng;
        }

        // Update or create marker
        if (marker) {
            marker.setLatLng(e.latlng);
        } else {
            marker = L.marker(e.latlng, { draggable: true }).addTo(map);

            // Update inputs when marker is dragged
            marker.on('dragend', function () {
                const position = marker.getLatLng();
                if (latInput && lngInput) {
                    latInput.value = position.lat;
                    lngInput.value = position.lng;
                }
                console.log('Marker dragged to:', position.lat, position.lng);
            });
        }

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
                        console.log('Reverse geocoded to:', data.display_name);
                    }
                })
                .catch(error => {
                    console.error('Error in reverse geocoding:', error);
                });
        }
    });
}