/**
 * Map functionality for location selection and map display
 * Uses Leaflet.js for map interaction
 * Works for both create post form and landing page map
 */
document.addEventListener('DOMContentLoaded', function () {
    console.log("Map.js loaded");

    // Function to initialize the create post map
    function initCreatePostMap() {
        console.log("Initializing location picker map");

        // Get the input fields
        const latitudeInput = document.getElementById('latitude');
        const longitudeInput = document.getElementById('longitude');
        const locationNameInput = document.getElementById('location_name');

        // Initialize the map with a default location
        const map = L.map('location-map').setView([51.505, -0.09], 13);

        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        // Create a marker variable to track the current selection
        let marker = null;

        // Try to get user's location
        if ("geolocation" in navigator) {
            navigator.geolocation.getCurrentPosition(function (position) {
                console.log("Got user location");
                // Center map on user's location
                map.setView([position.coords.latitude, position.coords.longitude], 13);

                // Set marker at user's location
                if (marker) {
                    marker.setLatLng([position.coords.latitude, position.coords.longitude]);
                } else {
                    marker = L.marker([position.coords.latitude, position.coords.longitude], { draggable: true }).addTo(map);
                    setupMarkerEvents(marker);
                }

                // Set the input values
                updateCoordinateFields(position.coords.latitude, position.coords.longitude);

                // Try reverse geocoding for location name
                reverseGeocode(position.coords.latitude, position.coords.longitude);
            }, function (error) {
                console.log("Error getting location:", error.message);
            });
        }

        // Handle map clicks to set/move the marker
        map.on('click', function (e) {
            console.log("Map clicked at:", e.latlng.lat, e.latlng.lng);

            // Set or move marker
            if (marker) {
                marker.setLatLng(e.latlng);
            } else {
                marker = L.marker(e.latlng, { draggable: true }).addTo(map);
                setupMarkerEvents(marker);
            }

            // Update input fields with location
            updateCoordinateFields(e.latlng.lat, e.latlng.lng);

            // Try reverse geocoding for location name
            reverseGeocode(e.latlng.lat, e.latlng.lng);
        });

        // Set up events for marker
        function setupMarkerEvents(marker) {
            marker.on('dragend', function (e) {
                const pos = marker.getLatLng();

                // Update input fields
                updateCoordinateFields(pos.lat, pos.lng);

                // Update location name via reverse geocoding
                reverseGeocode(pos.lat, pos.lng);
            });
        }

        // Function to update the coordinate fields
        function updateCoordinateFields(lat, lng) {
            if (latitudeInput && longitudeInput) {
                latitudeInput.value = lat;
                longitudeInput.value = lng;

                // Log the values to verify they are being set
                console.log("Set input field values - latitude:", latitudeInput.value, "longitude:", longitudeInput.value);
            } else {
                console.error("Coordinate input fields not found!");
            }
        }

        // Simple reverse geocoding using Nominatim
        function reverseGeocode(lat, lng) {
            const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`;

            fetch(url)
                .then(response => response.json())
                .then(data => {
                    console.log("Reverse geocoded to:", data.display_name);
                    if (locationNameInput && data.display_name) {
                        locationNameInput.value = data.display_name;
                    }
                })
                .catch(error => {
                    console.error("Error reverse geocoding:", error);
                });
        }

        // Check for existing coordinates (for edit mode)
        if (latitudeInput && longitudeInput && latitudeInput.value && longitudeInput.value) {
            const lat = parseFloat(latitudeInput.value);
            const lng = parseFloat(longitudeInput.value);

            if (!isNaN(lat) && !isNaN(lng)) {
                // Center map on existing coordinates
                map.setView([lat, lng], 13);

                // Set marker
                marker = L.marker([lat, lng], { draggable: true }).addTo(map);
                setupMarkerEvents(marker);
            }
        }

        return map;
    }

    // Function to initialize the landing page map
    function initLandingPageMap() {
        console.log("Initializing landing page map");

        // Initialize the map with a default location
        const map = L.map('map-view').setView([51.505, -0.09], 7);

        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        // Try to get user's location to center the map
        if ("geolocation" in navigator) {
            navigator.geolocation.getCurrentPosition(function (position) {
                map.setView([position.coords.latitude, position.coords.longitude], 10);
            }, function (error) {
                console.log("Error getting location:", error.message);
            });
        }

        // Load post locations if the function exists
        if (typeof loadPostLocations === 'function') {
            loadPostLocations(map);
        } else {
            // Fallback: try to load directly
            try {
                fetch('/post/api/post-locations/')
                    .then(response => response.json())
                    .then(data => {
                        console.log("Loaded post locations:", data);
                        if (data.posts && data.posts.length > 0) {
                            data.posts.forEach(post => {
                                addPostMarker(map, post);
                            });

                            // If we have posts, fit the map to their bounds
                            if (data.posts.length > 0) {
                                const bounds = L.latLngBounds(data.posts.map(post => [post.latitude, post.longitude]));
                                map.fitBounds(bounds, { padding: [50, 50] });
                            }
                        } else {
                            console.log("No post locations to display");
                        }
                    })
                    .catch(error => {
                        console.error("Error loading post locations:", error);
                    });
            } catch (e) {
                console.error("Error trying to load post locations:", e);
            }
        }

        return map;
    }

    // Helper function to add a post marker to the map
    function addPostMarker(map, post) {
        if (!post.latitude || !post.longitude) return;

        // Create marker
        const marker = L.marker([post.latitude, post.longitude]).addTo(map);

        // Add popup with post info
        marker.bindPopup(`
            <strong>${post.title}</strong>
            ${post.location_name ? `<br>${post.location_name}` : ''}
            <br><a href="/post/${post.id}/">View Post</a>
        `);
    }

    // Check which map we need to initialize
    const createPostMap = document.getElementById('location-map');
    const landingMap = document.getElementById('map-view');

    if (createPostMap) {
        initCreatePostMap();
    } else if (landingMap) {
        initLandingPageMap();
    } else {
        console.log("No map container found on this page");
    }
});